from googlesearch import search
from selenium import webdriver
import os
import re
import concurrent.futures
from sentence_transformers import SentenceTransformer, util
from bs4 import BeautifulSoup
import requests
import json
import SemanticSearchParallel
import base64
import get_api_data

# Specify the path to the Microsoft Edge WebDriver
edge_driver_path = 'E:/Simentic Search/edgedriver_win64/msedgedriver.exe'
os.environ["PATH"] += os.pathsep + edge_driver_path
# Configure the Edge webdriver
options = webdriver.EdgeOptions()
options.use_chromium = True
options.add_argument("--headless")

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
}

def main(medicine_name_query):
    # Define the allowed special symbols as a string
    allowed_symbols = "-'[]{}+&.()/,0123456789"

    # Create a pattern for allowed characters
    pattern = f'[^a-zA-Z\s{re.escape(allowed_symbols)}]'

    # Remove special symbols except the allowed ones
    medicine_name_query = re.sub(pattern, '', medicine_name_query)
    print(f"Removes symbols: {medicine_name_query}")
    outputReturn=""

    correctName = correct_spelling(medicine_name_query)
    print(f"Browser Return: {correctName}")

    # return correctName
    if "No suggestion found for" not in correctName:
        correctName = correctName.replace(" medicine used for?","")
        medicine_name_query = correctName.strip()
    
    print(f"Spell correction: {medicine_name_query}")

    medicine_name_query = medicine_name_query.title()
    print(f"TitleCase: {medicine_name_query}")

    form_data = {
        "function_name": "medicineDataExist",
        "med_name":medicine_name_query
    }
    response = requests.post(SemanticSearchParallel.API_URL, headers=get_api_data.headers, data=form_data)
    if response.status_code == 200:
        outputReturn = json.loads(response.text)
        if "info" in outputReturn:
            return outputReturn
        elif "error" in outputReturn:
            return outputReturn
    else:
        return {"error":response.text}
    
    scraped_medicine_data = get_info_from_google2(medicine_name_query)

    if(scraped_medicine_data==""):
        scraped_medicine_data = get_info_from_google(medicine_name_query)
    
    if(scraped_medicine_data==""):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            oneMG_future = executor.submit(search_google, medicine_name_query+" site:1mg.com")
            drugsCom_future = executor.submit(search_google, medicine_name_query+" site:drugs.com")
            rxlistCom_future = executor.submit(search_google, medicine_name_query+" site:rxlist.com")

            oneMGUrl = oneMG_future.result()
            drugsComUrl = drugsCom_future.result()
            rxlistComUrl = rxlistCom_future.result()

        docList = [oneMGUrl, drugsComUrl, rxlistComUrl]

        resultSimilarity = find_similarity(docList, medicine_name_query)

        print(resultSimilarity)

        if resultSimilarity[0] == oneMGUrl:
            scraped_medicine_data = oneMGExtractInfo(oneMGUrl)
        elif resultSimilarity[0] == drugsComUrl:
            scraped_medicine_data = drugsComExtractInfo(drugsComUrl)
        else:
            scraped_medicine_data = rxlistComExtractInfo(rxlistComUrl)

    # return {medicine_name_query:scraped_medicine_data,"status":"Success"}

    # return scraped_medicine_data

    scraped_medicine_data = base64.b64encode(scraped_medicine_data.encode('utf-8'))
    
    outputReturn=""
    form_data = {
        "function_name": "insertMedicineData",
        "med_name":medicine_name_query,
        "med_document":scraped_medicine_data
    }
    response = requests.post(SemanticSearchParallel.API_URL, headers=get_api_data.headers, data=form_data)
    if response.status_code == 200:
        outputReturn = json.loads(response.text)
    else:
        outputReturn = {"error":response.text}
    
    return outputReturn

def find_similarity(documents,query):
    # Load a pre-trained model (e.g., 'bert-base-nli-mean-tokens')
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Encode the documents into embeddings
    document_embeddings = model.encode(documents, convert_to_tensor=True)

    # Encode the query into an embedding
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Use cosine similarity to find the most similar documents
    cosine_scores = util.pytorch_cos_sim(query_embedding, document_embeddings)[0]

    # Sort the documents by similarity score (in descending order)
    sorted_results = sorted(enumerate(cosine_scores), key=lambda x: x[1], reverse=True)

    result=[]
    
    for i, score in sorted_results:
        result.append(documents[i])
    return result

def search_google(query, num_results=1):
    search_results = search(query, num=num_results, stop=num_results)
    return next(search_results, None)

def removeHTMLTags(inputString):
    pattern = re.compile(r'<.*?>')
    return re.sub(pattern, ' ', inputString)

def get_info_from_google(query):
    url = f"https://www.google.com/search?q={query}+used+for%3F&oq={query}+used+for%3F"

    html = requests.get(url=url,headers=header)

    soup = BeautifulSoup(html.text, "html.parser")
    spans = soup.find_all('span', class_='hgKElc')
    if spans:
        return " ".join([span.get_text() for span in spans])
    else:
        return ""
    
    # driver = webdriver.Edge(options=options)

    # # Load the webpage
    # driver.get(url)
    # res = driver.page_source
    # driver.quit()
    

    # soup = BeautifulSoup(res, "html.parser")
    # spans = soup.find_all('span', class_='hgKElc')
    # if spans:
    #     return " ".join([span.get_text() for span in spans])
    # else:
    #     return ""
    
def get_info_from_google2(query):
    url = f"https://www.google.com/search?q={query}+medicine+used+for%3F&oq={query}+medicine+used+for%3F"


    html = requests.get(url=url,headers=header)

    soup = BeautifulSoup(html.text, "html.parser")
    spans = soup.find_all('span', class_='hgKElc')
    if spans:
        return " ".join([span.get_text() for span in spans])
    else:
        return ""

    # driver = webdriver.Edge(options=options)

    # # Load the webpage
    # driver.get(url)
    # res = driver.page_source
    # driver.quit()
    

    # soup = BeautifulSoup(res, "html.parser")
    # spans = soup.find_all('span', class_='hgKElc')
    # if spans:
    #     return " ".join([span.get_text() for span in spans])
    # else:
    #     return ""

def drugsComExtractInfo(url):
    
    # driver = webdriver.Edge(options=options)

    # # Load the webpage
    # driver.get(url)
    # res = driver.page_source
    # driver.quit()
    html = requests.get(url=url,headers=header)
    res = html.text

    # Execute the tasks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future1 = executor.submit(drugsComExtractTask1, res)
        future2 = executor.submit(drugsComExtractTask2, res)
        future3 = executor.submit(drugsComExtractTask3, res)

        # Get results
        element_text1 = future1.result()
        element_text2 = future2.result()
        element_text3 = future3.result()


    # Regular expression pattern
    # pattern = r'<h2 id="uses"(.*?)>(.*?)</h2>(.*?)<h2(.*?)'

    # Find the match
    # matches = re.findall(pattern, res, re.DOTALL)
    # element_text = ""
    # if matches:
    #     for match in matches:
    #         element_text += " ".join(match)
    # else:
    #     pattern = r'<div class="contentBox">(.*?)<h2(.*?)>(.*?)</h2>(.*?)<h2(.*?)>'
    #     # Find the match
    #     matches = re.findall(pattern, res, re.DOTALL)
    #     if(matches):
    #         for match in matches:
    #             element_text += " ".join(match)
    #     else:
    #         pattern = r'<p class="Highlighta">(.*?)</p>'
    #         matches = re.findall(pattern, res, re.DOTALL)
    #         if(matches):
    #             for match in matches:
    #                 element_text += " ".join(match)
    if(element_text3!=""):
        element_text=element_text3
    elif(element_text2!=""):
        element_text=element_text2
    else:
        element_text = element_text1
    if(element_text!=""):
        # Regular expression pattern
        pattern = r'<p>(.*?)</p>'

        # Find all matches
        matches = re.findall(pattern, element_text, re.DOTALL)

        if matches:
            element_text = ""
            # Print the matches
            for match in matches:
                element_text += match+" "

        element_text = removeHTMLTags(element_text)

    # Remove unnecessary spaces, tabs, and newlines
    clean_string = re.sub(r'\s+', ' ', element_text).strip()
    return clean_string

def drugsComExtractTask1(res):
    pattern = r'<h2 id="uses"(.*?)>(.*?)</h2>(.*?)<h2(.*?)'
    matches = re.findall(pattern, res, re.DOTALL)
    element_text1 = ""
    if matches:
        for match in matches:
            element_text1 += " ".join(match)
    return element_text1

def drugsComExtractTask2(res):
    pattern = r'<div class="contentBox">(.*?)<h2(.*?)>(.*?)</h2>(.*?)<h2(.*?)>'
    matches = re.findall(pattern, res, re.DOTALL)
    element_text2 = ""
    if matches:
        for match in matches:
            element_text2 += " ".join(match)
    return element_text2

def drugsComExtractTask3(res):
    pattern = r'<p class="Highlighta">(.*?)</p>'
    matches = re.findall(pattern, res, re.DOTALL)
    element_text3 = ""
    if matches:
        for match in matches:
            element_text3 += " ".join(match)
    return element_text3



def oneMGExtractInfo(url):
    
    # driver = webdriver.Edge(options=options)

    # # Load the webpage
    # driver.get(url)
    # res = driver.page_source
    # driver.quit()

    html = requests.get(url=url,headers=header)
    res = html.text
    
    # pattern = r'<div\s+class="GenericSaltStyle__fCol___2RzoX\s+GenericSaltStyle__text-small___3trXZ">(.*?)<\/div>'

    # matches = re.findall(pattern, str(res))
    # element_text = ""
    # if matches:
    #     for match in matches:
    #         element_text += match+" "
    # else:
    #     pattern = r"<div class=\"DrugOverview__content___22ZBX\">(.*?)</div>"
    #     matches = re.findall(pattern, str(res))
    #     if matches:
    #         for matchitem in matches:
    #             element_text += matchitem+" "
    #     else:
    #         pattern = r'<div class="ProductDescription__description-content___A_qCZ"(.*?)>(.*?)</div>'
    #         matches = re.findall(pattern, str(res))
    #         if matches:
    #             for matchitem in matches:
    #                 element_text += " ".join(matchitem)

    # Run tasks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future1 = executor.submit(oneMGExtractTask1, res)
        future2 = executor.submit(oneMGExtractTask2, res)
        future3 = executor.submit(oneMGExtractTask3, res)

        element_text1 = future1.result()
        # print("Element 1: "+element_text1)
        # print("\n\n\n")
        element_text2 = future2.result()
        # print("Element 2: "+element_text2)
        # print("\n\n\n")
        element_text3 = future3.result()
        # print("Element 3: "+element_text3)
        # print("\n\n\n")

    if(element_text3!=""):
        element_text=element_text3
    elif(element_text2!=""):
        element_text=element_text2
    else:
        element_text = element_text1
    element_text = removeHTMLTags(element_text)

    # Remove unnecessary spaces, tabs, and newlines
    clean_string = re.sub(r'\s+', ' ', element_text).strip()
    return clean_string

def oneMGExtractTask1(res):
    pattern = r'<div\s+class="GenericSaltStyle__fCol___2RzoX\s+GenericSaltStyle__text-small___3trXZ">(.*?)<\/div>'
    matches = re.findall(pattern, res)
    element_text1 = ""
    if matches:
        for match in matches:
            element_text1 += match + " "
    return element_text1

def oneMGExtractTask2(res):

    # Extract data from the specific class of div tags
    soup = BeautifulSoup(res, 'html.parser')
    results = soup.find_all('div', class_='DrugOverview__content___22ZBX')

    # Iterate through the results and extract the data
    element_text2 = ""
    for result in results:
        element_text2 += result.text.strip() + " "

    # pattern = r'<div class="DrugOverview__content___22ZBX">(.*?)</div>'
    # matches = re.findall(pattern, res)
    # element_text2 = ""
    # if matches:
    #     for matchitem in matches:
    #         element_text2 += matchitem + " "
    return element_text2

def oneMGExtractTask3(res):
    # Extract data from the specific class of div tags
    soup = BeautifulSoup(res, 'html.parser')
    results = soup.find_all('div', class_='ProductDescription__description-content___A_qCZ')

    # Iterate through the results and extract the data
    element_text3 = ""
    for result in results:
        element_text3 += result.text.strip() + " "

    # pattern = r'<div class="ProductDescription__description-content___A_qCZ">(.*?)</div>'
    # matches = re.findall(pattern, res)
    # element_text3 = ""
    # if matches:
    #     for matchitem in matches:
    #         element_text3 += " ".join(matchitem)
    return element_text3



def rxlistComExtractInfo(url):
    # driver = webdriver.Edge(options=options)

    # # Load the webpage
    # driver.get(url)
    # res = driver.page_source
    # driver.quit()

    html = requests.get(url=url,headers=header)
    res = html.text
    
    # Extract data from the specific class of div tags
    soup = BeautifulSoup(res, 'html.parser')
    results = soup.find_all('div', class_='monograph_cont')

    # Iterate through the results and extract the data
    element_text = ""
    for result in results:
        element_text += result.text.strip() + " "

    element_text = removeHTMLTags(element_text)
    return element_text

def replace_spaces_with_plush(input_string):
    return input_string.replace(' ', '+')

def remove_multiple_spaces(input_string):
    # Use a regular expression to replace multiple spaces with a single space
    cleaned_string = re.sub(r'\s+', ' ', input_string)
    return cleaned_string.strip()

def format_google_query(query, reverse):

    # Replace other symbols with URL-encoded equivalents
    symbol_replacements = {
        '&': '%26',
        '@': '%40',
        '#': '%23',
        '%': '%25',
        '+': '%2B',
        '=': '%3D',
        '?': '%3F',
        '/': '%2F',
        '\\': '%5C',
        '|': '%7C',
        '<': '%3C',
        '>': '%3E',
        '{': '%7B',
        '}': '%7D',
        '[': '%5B',
        ']': '%5D',
        '^': '%5E',
        '`': '%60',
        ';': '%3B',
        ':': '%3A',
        ',': '%2C',
        '"': '%22',
        "'": '%27',
        '(': '%28',
        ')': '%29',
        '*': '%2A',
        '!': '%21',
        '~': '%7E',
    }

    if(reverse):
        for symbol, replacement in symbol_replacements.items():
            query = query.replace(replacement, symbol)
    else:
        for symbol, replacement in symbol_replacements.items():
            query = query.replace(symbol, replacement)

    return query


def correct_spelling(query):
    query = remove_multiple_spaces(query)
    print(f"Removes Multiple Spaces: {query}")
    query = format_google_query(query,False)
    print(f"Format Google Query: {query}")
    formatted_query = replace_spaces_with_plush(query)
    print(f"Replace Space with `+`: {formatted_query}")
    url = f"https://www.google.com/search?q={formatted_query}+medicine+used+for%3F"


    html = requests.get(url=url,headers=header)

    soup = BeautifulSoup(html.text, "html.parser")
    suggestion = soup.find("a", class_="gL9Hy")
    if suggestion:

        return format_google_query(suggestion.text,True)
    else:
        return f"No suggestion found for {query}."
    
    # driver = webdriver.Edge(options=options)

    # # Load the webpage
    # driver.get(url)
    # res = driver.page_source
    # driver.quit()

    # soup = BeautifulSoup(res, "html.parser")
    # suggestion = soup.find("a", class_="gL9Hy")
    # if suggestion:
    #     return suggestion.text
    # else:
    #     return f"No suggestion found for {query}."
