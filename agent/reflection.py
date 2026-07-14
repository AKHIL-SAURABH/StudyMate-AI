"""
StudyMate AI — Self-Reflection Module.

Reviews the agent's draft answer against quality criteria
and returns an improved version before delivery.
"""

from agent.llm_client import llm_client
from agent.prompts.reflection_prompt import get_reflection_prompt
from utils.logger import get_logger

logger = get_logger("reflection")


class ReflectionEngine:
    """
    Self-reflection engine that reviews and improves agent responses.

    Before delivering the final answer, the agent reflects on its
    response quality using an LLM call with a specialized prompt.
    """

    async def reflect(
        self,
        draft_answer: str,
        original_question: str,
        tools_used: list[str],
    ) -> str:
        """
        Reflect on and improve a draft answer.

        Args:
            draft_answer: The agent's initial response.
            original_question: The student's original question.
            tools_used: List of tool names used during reasoning.

        Returns:
            Improved response after reflection.
        """
        if not draft_answer.strip():
            logger.warning("Empty draft answer — skipping reflection")
            return "I apologize, but I wasn't able to generate a helpful response. Could you rephrase your question?"

        tools_str = ", ".join(tools_used) if tools_used else "None"

        reflection_prompt = get_reflection_prompt(
            draft_answer=draft_answer,
            original_question=original_question,
            tools_used=tools_str,
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a quality reviewer for an AI study mentor. "
                    "Review the draft response and return an improved version. "
                    "Return ONLY the improved response text."
                ),
            },
            {"role": "user", "content": reflection_prompt},
        ]

        try:
            improved = await llm_client.generate(
                messages, temperature=0.4, max_tokens=3000
            )

            if improved and len(improved.strip()) > 20:
                logger.info(
                    "Reflection improved response (draft=%d chars, improved=%d chars)",
                    len(draft_answer),
                    len(improved),
                )
                return improved.strip()

            logger.warning("Reflection returned inadequate response, using draft")
            return draft_answer

        except Exception as exc:
            logger.warning("Reflection failed (%s), using draft answer", exc)
            return draft_answer


# Singleton instance
reflection_engine = ReflectionEngine()
