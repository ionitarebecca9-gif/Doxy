import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

from ai_agent import ask_agent
from document_processing import process_document, delete_document_from_db

app = Flask(__name__)
CORS(app) 

os.makedirs("uploads", exist_ok=True) 

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('message', '')
    history = data.get('history', []) 
    
    if not question:
        return jsonify({"error": "Message is empty"}), 400
        
    try:
        result = ask_agent(question, history)
        return jsonify(result)
    except Exception as e:
        print("\nCHAT ERROR:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file received"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    save_path = os.path.join("uploads", file.filename)
    file.save(save_path)
    
    try:
        chunks_count = process_document(save_path)
        return jsonify({
            "success": True, 
            "filename": file.filename,
            "message": f"File processed successfully. Split into {chunks_count} chunks."
        })
    except Exception as e:
        print("\nUPLOAD ERROR:")
        traceback.print_exc() 
        return jsonify({"error": str(e)}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def route_delete(filename):
    try:
        delete_document_from_db(filename)
        return jsonify({"message": f"{filename} was successfully deleted."}), 200
    except Exception as e:
        print("\nDELETE ERROR:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        files = os.listdir("uploads")
        return jsonify({"documents": files})
    except Exception as e:
        return jsonify({"documents": [], "error": str(e)})
    
if __name__ == '__main__':
    print("Server is running on http://localhost:5000")
    app.run(port=5000, debug=False)