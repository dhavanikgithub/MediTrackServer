import concurrent.futures
import json
from sentence_transformers import SentenceTransformer, util
from flask import jsonify
import requests
import get_api_data

# Define a threshold score
SCORE_THRESHOLD = 0.34

API_URL = 'https://leavemanagementuvpce.000webhostapp.com/MediTrack/auth.php'

# Initialize the SentenceTransformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def find(query):
    # Define the form data as a dictionary
    form_data = {
        "function_name": "medicineData"
    }
    documents = []
    names = []
    response = requests.post(API_URL, headers=get_api_data.headers, data=form_data)
    if response.status_code == 200:
        my_dict = json.loads(response.text)
        for i in my_dict:
            documents.append(i["documents"])
            names.append(i["name"])
    else:
        return f"Request failed with status code: {response.text}"

    # Split the documents and names into chunks for multithreading
    chunk_size = 3
    document_chunks = [documents[i:i + chunk_size] for i in range(0, len(documents), chunk_size)]
    name_chunks = [names[i:i + chunk_size] for i in range(0, len(names), chunk_size)]

    # Process the document chunks using multithreading
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_chunk, chunk, query, name) for chunk, name in zip(document_chunks, name_chunks)]
        for future in concurrent.futures.as_completed(futures):
            results.extend(future.result())

    # Sort the results in descending order based on the score
    results.sort(key=lambda x: x['Score'], reverse=True)

    if not results or results[0]['Score'] < SCORE_THRESHOLD:
        results = [{"Name": "No records found", "Document": "No records found", "Score": 0}]

    # Return the sorted results
    return jsonify(results)

# Function to process document chunks
def process_chunk(chunk, query, names):
    document_embeddings = model.encode(chunk, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(query_embedding, document_embeddings)[0]
    result = []
    for i, score in enumerate(cosine_scores):
        if score.item() >= SCORE_THRESHOLD:
            doc = {
                "Name": names[i],
                "Document": chunk[i],
                "Score": score.item()
            }
            result.append(doc)
    return result