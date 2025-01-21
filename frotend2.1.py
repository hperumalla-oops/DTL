import streamlit as st
import random
import requests
from PyPDF2 import PdfReader
from pptx import Presentation
from docx import Document
import os
import base64
import webbrowser


def get_pdf_page_count(file_stream):
    try:
        # Create a PdfReader object from the file stream
        reader = PdfReader(file_stream)
        # Return the number of pages
        return len(reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None
    

def get_pptx_slide_count(file_stream):
        presentation = Presentation(file_stream)
        return len(presentation.slides)




# Title
st.title("File Upload and Specification Selector")

if st.button("View Queue"):
    url = "http://localhost:8501"
    webbrowser.open(url, new=0, autoraise=True)

# Input for UPI ID
upi_id = st.text_input("Enter your UPI ID", placeholder="e.g., yourname@upi")
file_To=0

# Upload multiple files
uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True, type=["pdf", "docx", "jpg", "png"])


if uploaded_files:
    file_details = []
    for file in uploaded_files:
        # Create a path to save the file
        
        file_content = file.read()
        encoded_file = base64.b64encode(file_content).decode('utf-8')
        
        # Save the file to the folder
        #with open(file_path, "wb") as f:
           # f.write(file.getbuffer())

        try:
            file_extension = file.name.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                page_count = get_pdf_page_count(file)

            elif file_extension in ['png', 'jpeg', 'jpg']:
                page_count = 1
            
            elif file_extension == 'pptx':
                page_count = get_pptx_slide_count(file)

            st.write(f"Pages: {page_count} for file {file.name}")

        except ValueError:
            pass

        # Specifications input for each file
    for index, uploaded_file in enumerate(uploaded_files):
        st.subheader(f"Specifications for {uploaded_file.name}")
        index=index+1
        binding = st.selectbox(f"Binding for {uploaded_file.name}", ["None", "Spiral", "Tape"], key=f"binding_{index}")
        paper = st.selectbox(f"Paper for {uploaded_file.name}", ["Regular", "Bond"], key=f"paper_{index}")
        size = st.selectbox(f"Size for {uploaded_file.name}", ["A3", "A4", "Passport"], key=f"size_{index}")
        color = st.selectbox(f"Color for {uploaded_file.name}", ["Colored", "Black-and-White"], key=f"color_{index}")
        side = st.selectbox(f"Side for {uploaded_file.name}", ["Single", "Double"], key=f"side_{index}")
        lamination = st.selectbox(f"Lamination for {uploaded_file.name}", ["Yes", "No"], key=f"lamination_{index}")
        copies = st.number_input(f"Copies for {uploaded_file.name}", min_value=1, step=1, key=f"copies_{index}")

        # Arbitrary cost generation logic
        cost = 0
        if size == 'A3':
            cost = 40 * page_count
        else:
            if color == 'Colored':
                cost = page_count * 5
            else:
                if side == 'Single':
                    cost = page_count
                else:
                    cost = page_count * 0.75
        if binding == 'Tape':
            cost += 5
        elif binding == 'Spiral':
            cost += 20
        if paper == "Bond":
            cost = cost + page_count * 3
        if lamination == 'Yes':
            cost += 30

        cost = cost * copies
        st.write(f"Generated Cost: ₹{cost}")

        file_details.append({
            #"File":encoded_file,
            "file_name": uploaded_file.name,
            "binding": binding,
            "paper": paper,
            "size": size,
            "color": color,
            "side": side,
            "lamination": lamination,
            "copies": copies,
            "cost": cost,
        })
        st.write(f"Please pay ₹{cost} to 7337702001")
    # Submit the data
    if st.button("Submit"):
        if not upi_id:
            st.error("Please enter a valid UPI ID.")
        else:
            for index, uploaded_file in enumerate(uploaded_files):
                # Prepare the JSON payload
                payload = {
                    "File":encoded_file,
                    "upi_id": upi_id,
                    "file_name": uploaded_file.name,
                    "specifications": file_details[index],
                }

                # Example server endpoint (replace with actual URL)
                server_url = "http://127.0.0.1:5000/upload"

                try:
                    # Send data to the server
                    with st.spinner("waiting for response, please do not close or reload this window"):
                        response = requests.post(server_url, json=payload)
                    
                    if response.status_code == 200:
                        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                    else:
                        st.error(f"Failed to upload '{uploaded_file.name}'. Server could not verify, please ensure payment is completed.")
                except Exception as e:
                    st.error(f"An error occurred while uploading '{uploaded_file.name}': {e}")

    
 