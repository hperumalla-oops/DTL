from flask import Flask, request, jsonify, redirect
from pymongo import MongoClient
from bson import ObjectId
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import re
from time import sleep
import streamlit as st
import pandas as pd
import base64
import threading


app = Flask(__name__)


def verify(upi_id, cost):


    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    #upi_id="SHVATANK VERMA"
    pattern_cost = r"Rs\.(\d+\.?\d*)"
    pat_name=r"from\s+([\w\s]+?)\s+Ref"

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:\\Users\\.a\\codes\\.vscode\\python\\dtl\\credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(userId='me', labelIds=['Label_93162935997077013']).execute()
    messages = results.get('messages', [])
    message_count = 4



    if not messages:
        print('No labels found.')
    else:
        

        for message in messages[:message_count]: 
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            snip=msg['snippet']
            print(snip)
            #print(upi_id)
            if snip:
                matche_cost = re.findall(pattern_cost, snip)
                matche_name = re.findall(pat_name, snip, re.IGNORECASE)
                print(upi_id)
                print(cost)
                print(matche_cost)
                print(matche_name)

                if matche_name[0].casefold()==upi_id.casefold() and int(matche_cost[0])==cost:

                    return True
                else:
                    continue

                #time.sleep(2)
        
    return False





app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Default URI for local MongoDB
db = client['file_upload_db']  # Replace with your DB name
collection = db['file_uploads']  



UPLOAD_FOLDER="downloads"
# Step 2: Fetch data from MongoDB
data = list(collection.find())  # Fetch all data (add filters if necessary)


# Step 3: Prepare a list of rows for the table
table_data = []



# Step 4: Loop through the data and create rows for the table


for record in data:
    specifications = record.get('specifications', {})
    
    # Extract specifications with default 'N/A' if not present
    row = {
        ## You can also customize this if needed
        'File Name': record.get('file_name', 'N/A'),
        'Verification': record.get('verified','N/A'),
        'Pages': record.get('page count', 'N/A'), # Adjust field name for file name
        'Binding': specifications.get('binding', 'N/A'),
        'Paper': specifications.get('paper', 'N/A'),
        'Size': specifications.get('size', 'N/A'),
        'Color': specifications.get('color', 'N/A'),
        'Side': specifications.get('side', 'N/A'),
        'Lamination': specifications.get('lamination', 'N/A'),
        'Copies': specifications.get('copies', 'N/A'),
        'Cost':specifications.get('cost','N/A')
    }
    table_data.append(row)

#print(table_data)

# Step 5: Convert the list of rows into a DataFrame
df = pd.DataFrame(table_data)
# Step 6: Apply custom CSS to resize the table
st.markdown("""
    <style>
        .streamlit-expanderHeader {
            font-size: 20px;
        }
        .stDataFrame {
            width: 100% !important;
        }
        .dataframe {
            width: 100% !important;
            max-width: 100% !important;
            table-layout: fixed;
        }
    </style>
""", unsafe_allow_html=True)

# Step 7: Display the data as a table in Streamlit
st.title("Specifications Table")

st.dataframe(df, width=100000   )



def insert_to_db(file_object):


    encoded=file_object.get("File")
    file_path = os.path.join(UPLOAD_FOLDER, file_object.get("file_name"))
    with open(file_path, "wb") as f:
            f.write(base64.b64decode(encoded))

    data = {

        "UPI_ID": file_object.get("upi_id"),
        "file_name": file_object.get("file_name"),
        "Encoded_File":file_object.get("File"),
        "specifications": file_object.get("specifications"),
        "verified": False  # Initially set to False
    }
    collection.insert_one(data)
    return True


@app.route('/upload', methods=['POST'])
def upload_file():
    print("weiojewerple[fple[pflefp[lefp[owij")
    file_object = request.json  # Assume the file object is sent as JSON
    if not file_object:
        return jsonify({"error": "No data received"}), 400
    ID= file_object.get("upi_id")
    cost=file_object.get("specifications")
    cost=cost.get("cost")
    i=0
    status=False
    while status == False and i < 5:
        print("here")
        status=verify(ID,cost)
        i=i+1
        print(i)
        # sleep(2)


    if status==True:
        insert_to_db(file_object)
        return jsonify({"Success": "Received"}), 200
    
    else:
        return jsonify({"Error": "Not Received"}), 400

    





if __name__ == "__main__":
    app.run( debug=False, port=5000)
