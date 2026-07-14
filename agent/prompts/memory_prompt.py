"""
StudyMate AI — Memory Prompt.

Summarizes long conversation histories into concise context
for maintaining continuity across sessions.
"""


MEMORY_SUMMARY_PROMPT = """Summarize the following conversation history into a concise context summary.
Focus on preserving:
1. Key facts about the student (subjects, topics, goals, exam dates)
2. Important decisions or plans made
3. Study progress and quiz scores mentioned
4. Any preferences expressed by the student

Keep the summary under 300 words. Be factual and concise.

## Conversation History:
{conversation_history}

## Summary:
"""


def get_memory_prompt(conversation_history: str) -> str:
    """
    Generate the memory summarization prompt.

    Args:
        conversation_history: Full conversation text to summarize.

    Returns:
        Formatted memory prompt.
    """
    return MEMORY_SUMMARY_PROMPT.format(conversation_history=conversation_history)
