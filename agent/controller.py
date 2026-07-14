"""
StudyMate AI — Agent Controller.

The main orchestrator that coordinates the complete agent pipeline:
1. Load memory/context
2. Discover MCP tools
3. Run ReAct loop
4. Apply self-reflection
5. Save memory and logs
6. Return response
"""

from typing import Optional

from agent.llm_client import llm_client
from agent.memory_manager import memory_manager
from agent.react_loop import react_loop
from agent.reflection import reflection_engine
from backend.models.chat import AgentStep, ChatResponse
from mcp_client.client import mcp_client
from utils.helpers import generate_id
from utils.logger import get_logger

logger = get_logger("controller")


class AgentController:
    """
    Main agent controller orchestrating the AI study mentor pipeline.

    Coordinates memory, tool discovery, ReAct reasoning, reflection,
    and persistence for each user interaction.
    """

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> ChatResponse:
        """
        Process a user message through the full agent pipeline.

        Pipeline:
        1. Generate/reuse conversation ID
        2. Load conversation context from memory
        3. Discover available MCP tools (dynamic)
        4. Run ReAct loop (Thought → Action → Observation → Repeat)
        5. Apply self-reflection to improve the answer
        6. Save conversation memory and agent logs
        7. Return structured response

        Args:
            user_id: Authenticated user ID.
            message: The student's message.
            conversation_id: Optional existing conversation ID.

        Returns:
            ChatResponse with the agent's answer and reasoning steps.
        """
        # Step 1: Conversation ID
        conv_id = conversation_id or generate_id()
        logger.info("Processing message for user=%s conv=%s", user_id, conv_id[:8])

        # Step 2: Load context
        context = await memory_manager.load_context(user_id, conv_id)

        # Step 3: Save user message to memory
        await memory_manager.save_message(user_id, conv_id, "user", message)

        # Step 4: Discover MCP tools dynamically
        try:
            await mcp_client.discover_tools()
            tools_description = mcp_client.get_tools_description()
            tools_list = mcp_client.get_tools_list_for_prompt()
            logger.info("Tools discovered: %d available", len(mcp_client.tools))
        except Exception as exc:
            logger.warning("Tool discovery failed: %s. Proceeding without tools.", exc)
            tools_description = "No tools available (MCP server unreachable)."
            tools_list = "No tools available."

        # Step 5: Run ReAct loop
        try:
            draft_answer, steps, tools_used = await react_loop.run(
                user_message=message,
                conversation_context=context,
                tools_description=tools_description,
                tools_list=tools_list,
            )
        except Exception as exc:
            logger.error("ReAct loop failed: %s", exc)
            draft_answer = (
                "I apologize, but I encountered an issue while processing your request. "
                "Could you try rephrasing your question? I'm here to help! 📚"
            )
            steps = []
            tools_used = []

        # Step 6: Self-reflection
        try:
            final_answer = await reflection_engine.reflect(
                draft_answer=draft_answer,
                original_question=message,
                tools_used=tools_used,
            )

            # Log the reflection step
            steps.append(AgentStep(
                step_number=len(steps) + 1,
                step_type="reflection",
                content="Answer reviewed and improved through self-reflection",
            ))

        except Exception as exc:
            logger.warning("Reflection failed: %s. Using draft answer.", exc)
            final_answer = draft_answer

        # Step 7: Save assistant response to memory
        await memory_manager.save_message(
            user_id, conv_id, "assistant", final_answer,
            metadata={"tools_used": tools_used},
        )

        # Step 8: Save agent logs
        for step in steps:
            await memory_manager.save_agent_log(
                user_id=user_id,
                conversation_id=conv_id,
                step_type=step.step_type,
                content=step.content,
                step_number=step.step_number,
                tool_name=step.tool_name,
                tool_input=step.tool_input,
                tool_output=step.tool_output,
            )

        logger.info(
            "Response generated: %d chars, %d steps, %d tools used",
            len(final_answer), len(steps), len(tools_used),
        )

        return ChatResponse(
            conversation_id=conv_id,
            response=final_answer,
            agent_steps=steps,
            tools_used=tools_used,
        )


# Singleton instance
agent_controller = AgentController()
