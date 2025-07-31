import os
import asyncio
import httpx
from httpx import AsyncClient, ReadTimeout

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = None
if GEMINI_API_KEY:
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

async def generate_gemini_summary(prompt: str) -> str:
    if not GEMINI_API_KEY or not GEMINI_API_URL:
        raise RuntimeError("GEMINI_API_KEY is not set in environment variables.")
    # Make the prompt even more explicit for Gemini
    detailed_prompt = (
        prompt +
        "\n\nYou are an expert meeting assistant. Write a long, detailed, multi-paragraph meeting preparation summary for the following event. "
        "Include: context, background, all key points, action items, and a thorough section of questions or discussion points relevant to the agenda. "
        "Use clear bullet points and paragraphs. Be verbose and detailed."
    )
    body = {
        "contents": [
            {
                "parts": [
                    {"text": detailed_prompt}
                ]
            }
        ]
    }
    import logging
    logger = logging.getLogger("gemini_api")
    import traceback
    try:
        logger.info("About to create httpx.AsyncClient and send request to Gemini API...")
        async with AsyncClient(timeout=30) as client:  # Increase timeout to 30 seconds
            for attempt in range(3):  # Retry logic: 3 attempts
                try:
                    logger.info(f"Sending prompt to Gemini (Attempt {attempt + 1}): {detailed_prompt}")
                    response = await client.post(GEMINI_API_URL, json=body)
                    logger.info(f"Gemini API HTTP status: {response.status_code}")
                    logger.info(f"Gemini API raw response: {response.text}")
                    response.raise_for_status()
                    data = response.json() if isinstance(response, httpx.Response) else await response.json()
                    logger.info(f"Gemini API response (parsed): {data}")
                    candidates = data.get("candidates", [])
                    summary = ""
                    if candidates and "content" in candidates[0]:
                        content = candidates[0]["content"]
                        if isinstance(content, dict) and "parts" in content:
                            parts = content["parts"]
                            summary = "\n".join(part.get("text", "") for part in parts if part.get("text"))
                        elif isinstance(content, str):
                            summary = content
                    else:
                        summary = data.get("text", "")
                    summary = summary.strip()
                    if not summary:
                        raise ValueError("Gemini returned empty summary")
                    if "question" not in summary.lower() and "discussion" not in summary.lower():
                        summary += "\n\nPrepare questions or discussion points relevant to the agenda."
                    return summary
                except ReadTimeout as timeout_exc:
                    logger.warning(f"Timeout occurred during Gemini API call (Attempt {attempt + 1}): {timeout_exc}")
                    if attempt == 2:  # Last attempt
                        raise
                except Exception as e:
                    logger.error(f"Error during Gemini API call (Attempt {attempt + 1}): {repr(e)}")
                    if attempt == 2:  # Last attempt
                        raise
    except Exception as e:
        logger.error(f"Gemini summary generation failed: {repr(e)}")
        logger.error(traceback.format_exc())
        # Fallback to default summary
        return "Main topic and agenda not available. Please review the meeting details and prepare questions or discussion points relevant to the agenda."

def summary_generate(prompt: str) -> str:
    """
    Synchronous wrapper for generate_gemini_summary for use in sync code or testing.
    """
    return asyncio.run(generate_gemini_summary(prompt))
