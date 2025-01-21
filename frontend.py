import streamlit as st
import random
import requests
from PyPDF2 import PdfReader
from pptx import Presentation
from docx import Document
import os
import base64
import webbrowser
from PIL import Image


def calculate_cost(specs):
    page_count = specs['page_count']
    size = specs['size']
    color = specs['color']
    side = specs['side']
    binding = specs['binding']
    paper = specs['paper']
    lamination = specs['lamination']
    copies = specs['copies']

    cost = 0
    if size == 'A3':
        cost = 40 * page_count
    elif size == "Passport":
        cost = 8
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
        cost += page_count * 3
    if lamination == 'Yes':
        cost += 30

    return cost * copies

def count_pages(file, file_extension):
    try:
        if file_extension == "pdf":
            pdf_reader = PdfReader(file)
            return len(pdf_reader.pages)
        elif file_extension == "pptx":
            presentation = Presentation(file)
            return len(presentation.slides)
        elif file_extension == "docx":
            document = Document(file)
            return len(document.paragraphs)  # Approximation for Word files
        elif file_extension == "png":
            img = Image.open(file)
            img.verify()  # Verify if the image is valid
            return 1
        else:
            return -1  # Unsupported file
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return -1




# Title
st.title("File Upload and Specification Selector")

# if st.button("View Queue"):
#     url = "http://localhost:8501"
#     webbrowser.open(url, new=0, autoraise=True)

#uploaded_files = st.file_uploader(
 #   "Upload your files (PDF, PNG, PPTX, DOCX)", 
  #  type=["pdf", "png", "pptx", "docx"], 
   # accept_multiple_files=True
#)

# Input for UPI ID
upi_id = st.text_input("Enter your Banking Name", placeholder="e.g., Vaivaswat Verma")
file_To=0

# Upload multiple files
uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True, type=["pdf", "docx", "jpg", "png"])
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if uploaded_files:
    file_details = []
    total_cost=0
    for file in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, file.name)
        file_content = file.read()
        encoded_file = base64.b64encode(file_content).decode('utf-8')
        

        file_extension = file.name.split('.')[-1].lower()
        page_count = count_pages(file, file_extension)


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


        specs={
            "name": uploaded_file.name,
            "type": file_extension.upper(),
            "page_count": page_count if page_count > 0 else "Unable to compute",
            "binding": binding,
            "paper": paper,
            "size": size,
            "color": color,
            "side": side,
            "lamination": lamination,
            "copies": copies
        }
        file_cost =calculate_cost(specs)
        total_cost+= file_cost
        file_details.append(specs)

        st.write(f"**Cost for {uploaded_file.name}: ₹{file_cost}**")
        st.write("---")

    for file_spec in file_details:
        file_spec['cost'] = total_cost


    # Submit the data
    if st.button("Submit"):
        with st.spinner("Uploading..."):
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
                    response = requests.post(server_url, json=payload)
                    if response.status_code == 200:
                        st.success(f"Files uploaded successfully!"
                       f"The total cost of your printouts is ₹{total_cost}. "
                        f"Please pay ₹{total_cost} to the following phone number: 99XXXXXXXXX (MR. Manoj, RVCE Printing). "
                        f"After payment, click on verify."
                        )

                    else:
                        st.error(f"Error uploading files: {response.json()}")
                except Exception as e:
                    st.error(f"An error occurred while uploading '{uploaded_file.name}': {e}")

    
 
