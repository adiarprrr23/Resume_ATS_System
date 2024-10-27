from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import fitz  # PyMuPDF
import io
import base64
import tempfile
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input_text, prompt, pdf_content[0]])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        first_page = doc.load_page(0)  # Load the first page
        pix = first_page.get_pixmap()  # Render page to Pixmap (image)

        # Create a temporary file for the PNG
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp_png:
            pix.save(tmp_png.name)  # Save as PNG to the temp file

            # Open the temporary PNG file with PIL and convert to JPEG
            with Image.open(tmp_png.name) as img:
                jpeg_byte_arr = io.BytesIO()
                img.convert("RGB").save(jpeg_byte_arr, format="JPEG")
                jpeg_byte_arr = jpeg_byte_arr.getvalue()

        pdf_parts = [
            {"mime_type": "image/jpeg", "data": base64.b64encode(jpeg_byte_arr).decode()}
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit UI
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")
submit4 = st.button("Percentage Match")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager with tech experience in Data Science, Full Stack Web Development, Big Data Engineering, DevOps, Data Analyst. Your task is to review the provided resume against the job description for these profiles.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
You are a skilled ATS (Application Tracking System) scanner with a deep understanding of Data Science, Full Stack Web Development, Big Data Engineering, DevOps, Data Analysis, and ATS functionality. Your task is to evaluate the resume against the provided job description.
Provide the percentage match if the resume matches the job description, list any missing keywords, and share final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt1)
        st.subheader("The Response is ")
        st.write(response)
    else:
        st.write("Please upload your resume")

elif submit4:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt2)
        st.subheader("The Response is ")
        st.write(response)
    else:
        st.write("Please upload your resume")
