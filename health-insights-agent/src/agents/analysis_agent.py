
from datetime import datetime, timedelta

import streamlit as st

from agents.model_manager import ModelManager
from config.app_config import ANALYSIS_DAILY_LIMIT


class AnalysisAgent:
    """Manage health report analysis and daily usage limits."""

    def __init__(self):
        self.model_manager = ModelManager()
        self._init_state()

    def _init_state(self):
        """Initialize analysis-related session state."""
        if "analysis_count" not in st.session_state:
            st.session_state.analysis_count = 0

        if "last_analysis" not in st.session_state:
            st.session_state.last_analysis = datetime.now()

        if "analysis_limit" not in st.session_state:
            st.session_state.analysis_limit = ANALYSIS_DAILY_LIMIT

        if "models_used" not in st.session_state:
            st.session_state.models_used = {}

    def check_rate_limit(self):
        """Check whether the daily analysis limit has been reached."""
        now = datetime.now()
        elapsed = now - st.session_state.last_analysis

        if elapsed >= timedelta(days=1):
            st.session_state.analysis_count = 0
            st.session_state.last_analysis = now
            return True, None

        if st.session_state.analysis_count >= st.session_state.analysis_limit:
            remaining = timedelta(days=1) - elapsed
            total_minutes = max(0, int(remaining.total_seconds() // 60))

            hours, minutes = divmod(total_minutes, 60)

            return False, (
                f"Daily analysis limit reached. "
                f"Please try again in {hours}h {minutes}m."
            )

        return True, None

    def analyze_report(
        self,
        data,
        system_prompt,
        check_only=False,
        chat_history=None
    ):
        """Analyze a report using the configured AI model."""
        can_analyze, error_msg = self.check_rate_limit()

        if not can_analyze:
            return {"success": False, "error": error_msg}

        if check_only:
            return can_analyze, error_msg

        processed_data = self._preprocess_data(data)

        enhanced_prompt = self._build_enhanced_prompt(
            system_prompt,
            chat_history
        )

        try:
            result = self.model_manager.generate_analysis(
                processed_data,
                enhanced_prompt
            )

            if result.get("success"):
                self._update_analytics(result)

            return result

        except Exception:
            return {
                "success": False,
                "error": (
                    "The analysis could not be completed. "
                    "Please check your AI configuration and try again."
                )
            }

    def _update_analytics(self, result):
        """Update usage statistics after successful analysis."""
        st.session_state.analysis_count += 1
        st.session_state.last_analysis = datetime.now()

        model_used = result.get("model_used", "unknown")

        st.session_state.models_used[model_used] = (
            st.session_state.models_used.get(model_used, 0) + 1
        )

    def _build_enhanced_prompt(self, system_prompt, chat_history):
        """Add context from the current conversation only."""
        enhanced_prompt = system_prompt

        if chat_history:
            session_context = self._get_session_context(chat_history)

            if session_context:
                enhanced_prompt += (
                    "\n\n## Current Conversation Context\n"
                    + session_context
                )

        return enhanced_prompt

    def _get_session_context(self, chat_history):
        """Extract the last two exchanges from the current conversation."""
        if not chat_history:
            return ""

        context_items = []

        for i in range(len(chat_history) - 1, 0, -1):
            previous = chat_history[i - 1]
            current = chat_history[i]

            if (
                previous.get("role") == "user"
                and current.get("role") == "assistant"
            ):
                user_msg = previous.get("content", "")
                ai_msg = current.get("content", "")

                user_msg = user_msg[:200]
                ai_msg = ai_msg[:200]

                context_items.append(
                    f"User: {user_msg}\nAssistant: {ai_msg}"
                )

                if len(context_items) >= 2:
                    break

        return "\n\n".join(reversed(context_items))

    def _preprocess_data(self, data):
        """Prepare report data for the AI model."""
        if isinstance(data, dict):
            return {
                "patient_name": data.get("patient_name", ""),
                "age": data.get("age", ""),
                "gender": data.get("gender", ""),
                "report": data.get("report", "")
            }

        return data
