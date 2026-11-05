import streamlit as st

from config.prompts import SPECIALIST_PROMPTS
from utils.pdf_extractor import extract_text_from_pdf
from config.sample_data import SAMPLE_REPORT
from config.app_config import MAX_UPLOAD_SIZE_MB


def show_analysis_form():
    st.subheader("ðŸ“„ Health Report Analysis")

    st.caption(
        "Upload a PDF report or explore the application "
        "using the sample report."
    )

    st.info(
        "Use synthetic or sample data while testing. "
        "Avoid uploading identifiable medical records."
    )

    if (
        "current_session" in st.session_state
        and "report_source" not in st.session_state
    ):
        st.session_state.report_source = "Upload PDF"

    report_source = st.radio(
        "Choose report source",
        ["Upload PDF", "Use Sample PDF"],
        index=(
            0
            if st.session_state.get("report_source") == "Upload PDF"
            else 1
        ),
        horizontal=True,
        key="report_source",
    )

    pdf_contents = get_report_contents(report_source)

    if pdf_contents:
        render_patient_form(pdf_contents)


def get_report_contents(report_source):
    if report_source == "Upload PDF":
        uploaded_file = st.file_uploader(
            f"Upload your health report (PDF, maximum {MAX_UPLOAD_SIZE_MB} MB)",
            type=["pdf"],
            help=(
                f"Maximum file size: {MAX_UPLOAD_SIZE_MB} MB. "
                "Only PDF files are supported."
            ),
        )

        if uploaded_file is not None:
            file_size_mb = uploaded_file.size / (1024 * 1024)

            if file_size_mb > MAX_UPLOAD_SIZE_MB:
                st.error(
                    f"File size ({file_size_mb:.1f} MB) exceeds "
                    f"the {MAX_UPLOAD_SIZE_MB} MB limit."
                )
                return None

            if uploaded_file.type != "application/pdf":
                st.error("Please upload a valid PDF file.")
                return None

            with st.spinner("Extracting text from your report..."):
                pdf_contents = extract_text_from_pdf(uploaded_file)

            if not isinstance(pdf_contents, str):
                st.error("Unable to extract text from the uploaded PDF.")
                return None

            if not pdf_contents.strip():
                st.error(
                    "No readable text was found. "
                    "Please use a text-based PDF report."
                )
                return None

            if pdf_contents.startswith(
                (
                    "File size exceeds",
                    "Invalid file type",
                    "Error validating",
                    "The uploaded file",
                )
            ) or "error" in pdf_contents.lower():
                st.error(pdf_contents)
                return None

            with st.expander("View Extracted Report"):
                st.text(pdf_contents)

            return pdf_contents

    else:
        with st.expander("View Sample Report"):
            st.text(SAMPLE_REPORT)

        return SAMPLE_REPORT

    return None


def render_patient_form(pdf_contents):
    st.markdown("### Patient Information")

    with st.form("analysis_form"):
        patient_name = st.text_input(
            "Patient Name",
            help="Use a fictional name when testing the application.",
        )

        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=18,
            )

        with col2:
            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"],
            )

        submitted = st.form_submit_button(
            "ðŸ” Analyze Health Report",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            handle_form_submission(
                patient_name,
                age,
                gender,
                pdf_contents,
            )


def handle_form_submission(
    patient_name,
    age,
    gender,
    pdf_contents,
):
    if not patient_name.strip():
        st.error("Please enter the patient name.")
        return

    from services.ai_service import generate_analysis

    can_analyze, error_msg = generate_analysis(
        None,
        None,
        check_only=True,
    )

    if not can_analyze:
        st.error(error_msg)
        return

    with st.spinner(
        "Analyzing the report. Please wait..."
    ):
        st.session_state.current_report_text = pdf_contents

        st.session_state.auth_service.save_chat_message(
            st.session_state.current_session["id"],
            f"Analyzing report for patient: {patient_name}",
        )

        result = generate_analysis(
            {
                "patient_name": patient_name,
                "age": age,
                "gender": gender,
                "report": pdf_contents,
            },
            SPECIALIST_PROMPTS["comprehensive_analyst"],
        )

        if result["success"]:
            report_metadata = (
                f"__REPORT_TEXT__\n"
                f"{pdf_contents}\n"
                f"__END_REPORT_TEXT__"
            )

            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"],
                report_metadata,
                role="system",
            )

            content = result["content"]

            if "model_used" in result:
                content += (
                    f"\n\n*Analysis generated using "
                    f"{result['model_used']}*"
                )

            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"],
                content,
                role="assistant",
            )

            st.rerun()

        else:
            st.error(
                result.get(
                    "error",
                    "An unexpected error occurred during analysis.",
                )
            )
