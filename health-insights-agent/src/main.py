import streamlit as st

from auth.session_manager import SessionManager
from components.auth_pages import show_login_page
from components.sidebar import show_sidebar
from components.analysis_form import show_analysis_form
from components.footer import show_footer
from config.app_config import (
    APP_NAME,
    APP_TAGLINE,
    APP_DESCRIPTION,
    APP_ICON,
    PRIMARY_COLOR,
)
from services.ai_service import get_chat_response


# Must be the first Streamlit command
st.set_page_config(
    page_title=f"{APP_NAME} - Health Report Assistant",
    page_icon=APP_ICON,
    layout="wide",
)

# Initialize session state
SessionManager.init_session()

# Custom application styling
st.markdown(
    f"""
    <style>
        div[data-testid="InputInstructions"] > span:nth-child(1) {{
            visibility: hidden;
        }}

        .healthmate-greeting {{
            text-align: right;
            padding: 1rem;
            color: {PRIMARY_COLOR};
            font-size: 1.1em;
            font-weight: 600;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


def show_welcome_screen():
    st.markdown(
        f"""
        <div style="text-align: center; padding: 50px 20px;">
            <h1>{APP_ICON} {APP_NAME}</h1>
            <h3>{APP_DESCRIPTION}</h3>
            <p style="font-size: 1.2em; color: #666;">
                {APP_TAGLINE}
            </p>
            <p>Start by creating a new analysis session.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 3, 2])

    with col2:
        if st.button(
            "âž• Create New Analysis Session",
            use_container_width=True,
            type="primary",
        ):
            success, session = SessionManager.create_chat_session()

            if success:
                st.session_state.current_session = session
                st.rerun()
            else:
                st.error("Failed to create session. Please try again.")


def show_chat_history():
    success, messages = st.session_state.auth_service.get_session_messages(
        st.session_state.current_session["id"]
    )

    if success:
        for msg in messages:
            # Skip system messages containing report metadata
            if msg.get("role") == "system":
                continue

            if msg["role"] == "user":
                st.info(msg["content"])
            else:
                st.success(msg["content"])

        return messages

    return []


def handle_chat_input(messages):
    prompt = st.chat_input(
        "Ask a follow-up question about the report..."
    )

    if prompt:
        # Display user message
        st.info(prompt)

        # Save user message
        st.session_state.auth_service.save_chat_message(
            st.session_state.current_session["id"],
            prompt,
            role="user",
        )

        # Retrieve report context
        context_text = st.session_state.get("current_report_text", "")

        # Restore report context from stored system message if needed
        if not context_text and messages:
            for msg in messages:
                if (
                    msg.get("role") == "system"
                    and "__REPORT_TEXT__" in msg.get("content", "")
                ):
                    content = msg.get("content", "")

                    marker = "__REPORT_TEXT__\n"
                    start_idx = content.find(marker) + len(marker)
                    end_idx = content.find("\n__END_REPORT_TEXT__")

                    if start_idx >= len(marker) and end_idx > start_idx:
                        context_text = content[start_idx:end_idx]
                        st.session_state.current_report_text = context_text
                        break

        with st.spinner("Preparing your response..."):
            response = get_chat_response(
                prompt,
                context_text,
                messages,
            )

            st.success(response)

            # Save assistant response
            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"],
                response,
                role="assistant",
            )

            st.rerun()


def show_user_greeting():
    if st.session_state.user:
        display_name = (
            st.session_state.user.get("name")
            or st.session_state.user.get("email", "")
        )

        st.markdown(
            f"""
            <div class="healthmate-greeting">
                ðŸ‘‹ Hi, {display_name}
            </div>
            """,
            unsafe_allow_html=True,
        )


def main():
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        show_login_page()
        show_footer()
        return

    # User greeting
    show_user_greeting()

    # Sidebar
    show_sidebar()

    # Main application area
    if st.session_state.get("current_session"):
        st.title(
            f"ðŸ“Š {st.session_state.current_session['title']}"
        )

        messages = show_chat_history()

        if messages:
            with st.expander(
                "New Analysis / Update Report",
                expanded=False,
            ):
                show_analysis_form()

            handle_chat_input(messages)

        else:
            show_analysis_form()

    else:
        show_welcome_screen()


if __name__ == "__main__":
    main()
