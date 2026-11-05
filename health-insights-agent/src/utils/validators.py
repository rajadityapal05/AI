
import re
from config.app_config import MAX_UPLOAD_SIZE_MB


def validate_password(password):
    """Validate password meets security requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    return True, None


def validate_email(email):
    """Validate email format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))


def validate_signup_fields(name, email, password, confirm_password):
    """Validate all signup form fields."""
    if not all([name, email, password, confirm_password]):
        return False, "Please fill in all fields"

    if not validate_email(email):
        return False, "Please enter a valid email address"

    if password != confirm_password:
        return False, "Passwords do not match"

    is_valid, error_msg = validate_password(password)

    if not is_valid:
        return False, error_msg

    return True, None


def validate_pdf_file(file):
    """Validate PDF file size, type, and file signature."""
    if file is None:
        return False, "No file uploaded"

    file_size = getattr(file, "size", 0)

    if file_size <= 0:
        return False, "The uploaded file is empty."

    file_size_mb = file_size / (1024 * 1024)

    if file_size_mb > MAX_UPLOAD_SIZE_MB:
        return False, (
            f"File size ({file_size_mb:.1f}MB) exceeds "
            f"the {MAX_UPLOAD_SIZE_MB}MB limit."
        )

    if getattr(file, "type", None) != "application/pdf":
        return False, "Invalid file type. Please upload a PDF file."

    try:
        file.seek(0)
        signature = file.read(5)
        file.seek(0)

        if signature != b"%PDF-":
            return False, "The uploaded file does not have a valid PDF signature."

    except (AttributeError, OSError):
        return False, "Unable to read the uploaded PDF file."

    return True, None


def validate_pdf_content(text):
    """Check whether extracted text contains medical-report indicators."""
    if not isinstance(text, str) or len(text.strip()) < 50:
        return False, (
            "Extracted text is too short. "
            "Please ensure the PDF contains readable text."
        )

    medical_terms = [
        "blood", "laboratory", "patient", "specimen",
        "reference range", "hemoglobin", "haemoglobin",
        "wbc", "rbc", "platelet", "glucose",
        "creatinine", "cholesterol", "diagnosis",
        "test result", "medical report", "urine",
        "thyroid", "vitamin", "hba1c"
    ]

    text_lower = text.lower()
    term_matches = sum(
        1 for term in medical_terms if term in text_lower
    )

    if term_matches < 2:
        return False, (
            "The document does not contain enough medical-report "
            "indicators. Please check that you selected the correct PDF."
        )

    return True, None
