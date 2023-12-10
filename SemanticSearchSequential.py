import json
from sentence_transformers import SentenceTransformer, util
from flask import jsonify
import requests
import get_api_data

API_URL  = 'https://leavemanagementuvpce.000webhostapp.com/MediTrack/auth.php'
SCORE_THRESHOLD = 0.34

def find(query):
    # Define the form data as a dictionary
    form_data = {
        "function_name": "medicineData"
    }
    documents=[]
    name=[]
    response = requests.post(API_URL, headers=get_api_data.headers, data=form_data)
    if response.status_code == 200:
        my_dict =  json.loads(response.text)
        for i in my_dict:
            documents.append(i["documents"])
            name.append(i["name"])
    else:
        return f"Request failed with status code: {response.text}"
    # Load a pre-trained model (e.g., 'bert-base-nli-mean-tokens')
    # model = SentenceTransformer('bert-base-nli-mean-tokens')
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Define a list of sentences or documents to search through
    # documents = [
    #     "Decongestants, such as pseudoephedrine and phenylephrine, can raise your blood pressure and heart rate. If you have high blood pressure, it's a good idea to check with your doctor or pharmacist to find out what's right for you. You can also try decongestant-free cold medicines, such as Coricidin HBP.",
    #     "Some early research suggests that zinc may ease your symptoms and shorten your cold. But other studies show that it doesn't work any better than a placebo ('dummy pill'). Also, the FDA warns that several zinc nasal sprays have been linked to a permanent loss of smell. For all these reasons, the side effects from zinc may outweigh any possible benefits.",
    #     "Children have special needs when it comes to cold medicine. Don't give over-the-counter cough and cold drugs to children under 4. Although kids' cold medicines may still be on the shelves at your drugstore, talk to your child's doctor before using them.",
    #     "The common cold leads to more healthcare provider visits and absences from school and work than any other illness each year. It is caused by any one of several viruses and is easily spread to others. It’s not caused by cold weather or getting wet.",
    #     "A cold is caused by any one of several viruses that causes inflammation of the membranes that line the nose and throat. It can result from any one of more than 200 different viruses. But, the rhinoviruses causes most colds.",
    #     "The common cold is very easily spread to others. It's often spread through airborne droplets that are coughed or sneezed into the air by the sick person. The droplets are then inhaled by another person. Colds can also be spread when a sick person touches you or a surface (like a doorknob) that you then touch.",
    #     "Everyone is at risk for the common cold. People are most likely to have colds during fall and winter, starting in late August or early September until March or April. The increased incidence of colds during the cold season may be attributed to the fact that more people are indoors and close to each other. In addition, in cold, dry weather, the nasal passages become drier and more vulnerable to infection.",
    #     "Children suffer more colds each year than adults, due to their immature immune systems and to the close physical contact with other children at school or day care. In fact, the average child will have between 6 to 10 colds a year. The average adult will get 2 to 4 colds a year.",
    #     "Common cold symptoms may include: 1) Stuffy, 2) runny nose 3) Scratchy, 4) tickly throat, 5) Sneezing, 6) Watering eyes, 7) Low-grade fever, 8) Sore throat, 9) Mild hacking cough, 10) Achy muscles and bones, 11) Headache, 12) Mild fatigue, 13) Chills Watery discharge from nose that thickens and turns yellow or green",
    #     "There are lots of different cold and cough medicines, and they do different things:1) Nasal decongestants - unclog a stuffy nose, 2) Cough suppressants - quiet a cough, 3) Expectorants - loosen mucus in your lungs so you can cough it up, 4) Antihistamines - stop runny noses and sneezing, 5) Pain relievers - ease fever, headaches, and minor aches and pains",
    #     "A cold is caused by a virus that causes inflammation of the membranes that line the nose and throat."
    # ]

    # Encode the documents into embeddings
    document_embeddings = model.encode(documents, convert_to_tensor=True)

    # Define a query
    # query = input("Query: ")

    # Encode the query into an embedding
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Use cosine similarity to find the most similar documents
    cosine_scores = util.pytorch_cos_sim(query_embedding, document_embeddings)[0]

    # Sort the documents by similarity score (in descending order)
    sorted_results = sorted(enumerate(cosine_scores), key=lambda x: x[1], reverse=True)

    # Print the most similar documents
    # top_k = result_needed  # Adjust this number to get more or fewer results
    result=[]
    # return sorted_results[:top_k]
    
    for i, score in sorted_results:
        if (score.item()>=SCORE_THRESHOLD):
            doc = {
                "Name": name[i],
                "Document": documents[i],
                "Score": score.item()  # Convert the Tensor to a NumPy array
            }
            result.append(doc)
            # print(f"Document {i + 1}: {documents[i]} (Similarity Score: {score:.4f})")
    if not result or result[0]['Score'] < SCORE_THRESHOLD:
        result = [{"Name": "No records found", "Document": "No records found", "Score": 0}]
    return jsonify(result)
