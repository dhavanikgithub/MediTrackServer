import requests
from bs4 import BeautifulSoup
import spacy

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase/credentials/meditrack-ed326-firebase-adminsdk-zwljt-ebea362d85.json")
firebase_admin.initialize_app(cred)
# Initialize Firestore
db = firestore.client()

def index():
    # Example: Query data from Firestore
    users_ref = db.collection('about_us')
    users = users_ref.get()
    user_data = [user.to_dict() for user in users]

    return user_data

def start_my_process(query):
    header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    html = requests.get(url=query,headers=header)

    # soup = BeautifulSoup(html.text, "html.parser")
    # spans = soup.find_all('span', class_='hgKElc')
    # if spans:
    #     return " ".join([span.get_text() for span in spans])
    # else:
    #     return ""
    

    soup = BeautifulSoup(html.text, 'html.parser')

    target_divs = soup.find_all('div', class_='style__font-bold___1k9Dl style__font-14px___YZZrf style__flex-row___2AKyf style__space-between___2mbvn style__padding-bottom-5px___2NrDR')

    all_med_name=[]
    if target_divs:
        for div in target_divs:
            inner_div = div.find('div')
            if inner_div:
                extracted_data = inner_div.get_text(strip=True)
                all_med_name.append(extracted_data)
    
    return "</br>".join(all_med_name)


