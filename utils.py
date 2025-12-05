import pypdf

def extract_pdf_text(uploaded_file):
    """Extracts text from a Streamlit UploadedFile object."""
    pdf_reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text