"""
StudyMate AI — ReAct Loop Engine.

Implements the Reasoning + Acting loop:
Thought → Action → Observation → Repeat → Final Answer

The LLM decides which tool to use (or to finish) at each step.
No hardcoded workflows — the agent reasons dynamically.
"""

import json
from typing import Any, Optional

from agent.llm_client import llm_client
from agent.prompts.system_prompt import get_system_prompt
from agent.prompts.tool_calling_prompt import get_tool_calling_prompt
from backend.config import get_settings
from backend.exceptions import MaxIterationsError, JSONParseError
from backend.models.chat import AgentStep
from mcp_client.client import mcp_client
from utils.logger import get_logger

logger = get_logger("react_loop")


class ReActLoop:
    """
    ReAct (Reasoning + Acting) loop engine.

    Drives the agent through iterative reasoning, tool calling,
    and observation cycles until a final answer is reached.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    async def run(
        self,
        user_message: str,
        conversation_context: list[dict[str, str]],
        tools_description: str,
        tools_list: str,
    ) -> tuple[str, list[AgentStep], list[str]]:
        """
        Execute the ReAct loop.

        Args:
            user_message: The student's current message.
            conversation_context: Previous conversation messages.
            tools_description: Full tool descriptions for system prompt.
            tools_list: Concise tool list for action prompts.

        Returns:
            Tuple of (final_answer, agent_steps, tools_used).

        Raises:
            MaxIterationsError: If max iterations exceeded without final answer.
        """
        max_iterations = self._settings.agent_max_iterations
        steps: list[AgentStep] = []
        tools_used: list[str] = []
        observations: list[str] = []

        # Build the system prompt with available tools
        system_prompt = get_system_prompt(tools_description)

        for iteration in range(1, max_iterations + 1):
            logger.info("ReAct iteration %d/%d", iteration, max_iterations)

            # Build context string including previous observations
            context = self._build_context(
                user_message, conversation_context, observations
            )

            # Ask the LLM for thought + action
            tool_prompt = get_tool_calling_prompt(tools_list, context)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": tool_prompt},
            ]

            parsed = await llm_client.generate_json(messages, temperature=0.3)

            if not parsed:
                logger.warning("Failed to parse LLM response in iteration %d", iteration)
                # If we have observations, try to synthesize a final answer
                if observations:
                    return self._synthesize_fallback(observations, user_message), steps, tools_used
                raise JSONParseError()

            thought = parsed.get("thought", "")
            action = parsed.get("action", "final_answer")
            action_input = parsed.get("action_input", {})

            # Log the thought step
            steps.append(AgentStep(
                step_number=iteration,
                step_type="thought",
                content=thought,
            ))

            logger.info("Thought: %s", thought[:100])
            logger.info("Action: %s", action)

            # Check if it's a final answer
            if action == "final_answer":
                answer = action_input.get("answer", "") if isinstance(action_input, dict) else str(action_input)
                steps.append(AgentStep(
                    step_number=iteration,
                    step_type="final",
                    content=answer,
                ))
                logger.info("Final answer reached at iteration %d", iteration)
                return answer, steps, tools_used

            # Execute the tool
            try:
                steps.append(AgentStep(
                    step_number=iteration,
                    step_type="action",
                    content=f"Calling tool: {action}",
                    tool_name=action,
                    tool_input=action_input if isinstance(action_input, dict) else {},
                ))

                tool_result = await mcp_client.call_tool(
                    action,
                    action_input if isinstance(action_input, dict) else {},
                )

                tools_used.append(action)

                # Log the observation
                observation = f"Tool '{action}' returned: {tool_result}"
                observations.append(observation)

                steps.append(AgentStep(
                    step_number=iteration,
                    step_type="observation",
                    content=tool_result[:500],
                    tool_name=action,
                    tool_output=tool_result,
                ))

                logger.info("Observation from %s: %s", action, tool_result[:100])

            except Exception as exc:
                error_msg = f"Tool '{action}' failed: {str(exc)}"
                observations.append(error_msg)
                steps.append(AgentStep(
                    step_number=iteration,
                    step_type="observation",
                    content=error_msg,
                    tool_name=action,
                ))
                logger.warning("Tool execution failed: %s", exc)

        # Exceeded max iterations — synthesize best possible answer
        logger.warning("Max iterations (%d) reached", max_iterations)

        if observations:
            answer = self._synthesize_fallback(observations, user_message)
            steps.append(AgentStep(
                step_number=max_iterations + 1,
                step_type="final",
                content=answer,
            ))
            return answer, steps, tools_used

        raise MaxIterationsError(max_iterations)

    def _build_context(
        self,
        user_message: str,
        conversation_context: list[dict[str, str]],
        observations: list[str],
    ) -> str:
        """Build the context string for the LLM."""
        parts = []

        # Include recent conversation
        if conversation_context:
            parts.append("### Recent Conversation:")
            for msg in conversation_context[-6:]:  # Last 6 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                parts.append(f"**{role}**: {content[:300]}")

        # Current message
        parts.append(f"\n### Current Student Message:\n{user_message}")

        # Previous observations in this loop
        if observations:
            parts.append("\n### Previous Tool Results (this conversation):")
            for i, obs in enumerate(observations, 1):
                parts.append(f"Step {i}: {obs[:500]}")

        return "\n".join(parts)

    def _synthesize_fallback(self, observations: list[str], user_message: str) -> str:
        """
        Create a fallback answer from observations when max iterations reached.

        Args:
            observations: List of tool observation strings.
            user_message: Original user message.

        Returns:
            Synthesized answer text.
        """
        obs_text = "\n".join(observations)
        return (
            f"Based on my analysis, here's what I found:\n\n{obs_text}\n\n"
            f"I gathered this information to help with your question about: {user_message[:200]}"
        )


# Singleton instance
react_loop = ReActLoop()
