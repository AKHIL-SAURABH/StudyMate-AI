"""
StudyMate AI — JSON Repair Prompt.

When the LLM produces malformed JSON, this prompt attempts
to get the LLM to fix and return valid JSON.
"""


JSON_REPAIR_PROMPT = """The following text was supposed to be valid JSON but has syntax errors.
Fix it and return ONLY the corrected, valid JSON. No explanations, no markdown, just the JSON object.

The expected format is:
{{
  "thought": "reasoning text",
  "action": "tool_name or final_answer",
  "action_input": {{}}
}}

## Malformed Text:
{malformed_json}

## Return ONLY valid JSON:
"""


def get_json_repair_prompt(malformed_json: str) -> str:
    """
    Generate the JSON repair prompt.

    Args:
        malformed_json: The malformed JSON string from the LLM.

    Returns:
        Formatted JSON repair prompt.
    """
    return JSON_REPAIR_PROMPT.format(malformed_json=malformed_json)
