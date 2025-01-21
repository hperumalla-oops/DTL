from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from werkzeug.utils import secure_filename
import os


UPLOAD_FOLDER = './uploaded_files'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'pptx', 'docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['print_service']
collection = db['uploaded_files']

@app.route('/upload', methods=['POST'])
def upload_files():

    # Check for required keys in the request
    if 'files' not in request.files or 'metadata' not in request.form:
        return jsonify({'error': 'Missing files or metadata'}), 400
    
    files = request.files.getlist('files')
    metadata = request.form.get('metadata')
    
    if not metadata:
        return jsonify({'error': 'No metadata provided'}), 400

    # Convert metadata from string to list of dictionaries
    metadata = eval(metadata)  # Ensure this is sanitized in production!
    uploaded_files = []

    for idx, file in enumerate(files):
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            # Save file locally
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Add file and metadata details to the database
            file_entry = {
                'filename': filename,
                'filepath': filepath,
                'metadata': metadata[idx]
            }
            collection.insert_one(file_entry)

            # Append to response
            uploaded_files.append(file_entry)

    return jsonify({'error': 'No metadata provided'}), 200



"""try:
        files = request.files.getlist('files')
        if 'files' not in request.files:
            return jsonify({'error': 'No files part'}), 400

        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400

        uploaded_files = []
        for file in files:
            if file.filename == '':
                continue
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append(filename)

        metadata = request.form.get('metadata')
        if not metadata:
            return jsonify({"error": "No metadata provided"}), 400

        try:
            metadata_list = json.loads(metadata)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid metadata format"}), 400

        if not isinstance(metadata_list, list):
            return jsonify({"error": "Metadata should be a list"}), 400

        for file_data in metadata_list:
            file_data['verification'] = "unchecked"  # Add verification status
            collection.insert_one(file_data)  # Save to MongoDB

        return jsonify({"message": "Files successfully uploaded"}), 200

    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except FileNotFoundError as e:
        return jsonify({"error": f"File error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500"""

@app.route('/verify', methods=['POST'])
def verify_files():
    try:
        # Perform verification logic (e.g., check payment status)
        verification_success = True  # Simulate verification outcome

        if verification_success:
            # Update all documents in MongoDB to set verification as "checked"
            collection.update_many({"verification": "unchecked"}, {"$set": {"verification": "checked"}})
            return jsonify({"message": "Verification successful"}), 200
        else:
            return jsonify({"message": "Verification failed"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
