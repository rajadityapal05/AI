
import logging
import streamlit as st
import groq

from enum import Enum

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    FALLBACK = "fallback"


class ModelManager:
    """Manage Groq AI models and automatic fallback."""

    MODEL_CONFIG = {
        ModelTier.PRIMARY: {
            "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
            "max_tokens": 2000,
            "temperature": 0.3
        },
        ModelTier.SECONDARY: {
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 2000,
            "temperature": 0.3
        },
        ModelTier.TERTIARY: {
            "model": "llama-3.1-8b-instant",
            "max_tokens": 2000,
            "temperature": 0.3
        },
        ModelTier.FALLBACK: {
            "model": "llama3-70b-8192",
            "max_tokens": 2000,
            "temperature": 0.3
        }
    }

    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Groq client."""
        try:
            api_key = st.secrets.get("GROQ_API_KEY")

            if not api_key:
                logger.warning("Groq API key is not configured.")
                return

            self.client = groq.Groq(api_key=api_key)

        except Exception:
            logger.exception("Could not initialize Groq client.")

    def generate_analysis(self, data, system_prompt, retry_count=0):
        """Generate an AI response with automatic model fallback."""

        if self.client is None:
            return {
                "success": False,
                "error": (
                    "AI service is not configured. "
                    "Please check GROQ_API_KEY in your Streamlit secrets."
                )
            }

        tiers = list(ModelTier)

        if retry_count >= len(tiers):
            return {
                "success": False,
                "error": (
                    "All configured AI models are currently unavailable. "
                    "Please try again later."
                )
            }

        tier = tiers[retry_count]
        config = self.MODEL_CONFIG[tier]

        # Do not send a patient name to the external AI provider.
        if isinstance(data, dict):
            safe_data = {
                key: value
                for key, value in data.items()
                if key != "patient_name"
            }
        else:
            safe_data = data

        safety_instructions = """
IMPORTANT RESPONSE GUIDELINES:
- Provide educational explanations, not medical diagnoses.
- Do not prescribe medicines or recommend changing treatment.
- Explain medical terms in clear, simple language.
- Distinguish reported values from general explanations.
- Do not invent missing test results or reference ranges.
- Mention when a value should be discussed with a qualified
  healthcare professional.
- If information is incomplete or unclear, say so.
- Never claim certainty when the report does not support it.
"""

        final_prompt = (
            system_prompt.strip()
            + "\n\n"
            + safety_instructions
        )

        try:
            logger.info("Trying configured model: %s", config["model"])

            completion = self.client.chat.completions.create(
                model=config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": final_prompt
                    },
                    {
                        "role": "user",
                        "content": str(safe_data)
                    }
                ],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )

            content = completion.choices[0].message.content

            if not content or not content.strip():
                raise ValueError("The AI model returned an empty response.")

            return {
                "success": True,
                "content": content,
                "model_used": f"groq/{config['model']}"
            }

        except Exception as error:
            logger.warning(
                "Model %s failed: %s",
                config["model"],
                str(error)
            )

            return self.generate_analysis(
                safe_data,
                system_prompt,
                retry_count + 1
            )
