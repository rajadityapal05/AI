
import streamlit as st
from config.app_config import APP_NAME, PRIMARY_COLOR


def show_footer(in_sidebar=False):
    footer_margin = "0" if in_sidebar else "2rem"

    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 0.75rem;
            margin-top: {footer_margin};
            border-top: 1px solid rgba(37, 99, 235, 0.15);
            width: 100%;
        ">
            <p style="
                color: {PRIMARY_COLOR};
                font-size: 0.8rem;
                margin: 0;
            ">
                🩺 <strong>{APP_NAME}</strong>
                <br>
                AI-assisted health report insights
            </p>

            <p style="
                color: #64748B;
                font-size: 0.7rem;
                margin-top: 8px;
            ">
                Built upon the open-source project
                <a href="https://github.com/harshhh28/hia"
                   target="_blank"
                   style="color: {PRIMARY_COLOR};">
                    HIA by Harsh Gajjar
                </a>
            </p>

            <p style="
                color: #64748B;
                font-size: 0.7rem;
                margin-top: 6px;
            ">
                For informational purposes only. Not a substitute
                for professional medical advice.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
