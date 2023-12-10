import requests
from bs4 import BeautifulSoup
import concurrent.futures
import os

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
}
def main():
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Parallel execution for each alphabet
        results = list(executor.map(process_label, alphabet))

    # totalUrlList = []
    # printOutput = []
    # for label, item in zip(alphabet, results):
    #     message = f"Label `{label}` no of urls: {len(item)}<br>"
    #     printOutput.append(message)
    #     totalUrlList.extend(item)
    # mainRes = f"Total no of Urls: {len(totalUrlList)}<br>"+"".join(printOutput)
    # # urlListRes = "<br>".join(results)
    # return f"{mainRes}<br>"

    index = 24

    my_label = results[index]

    # Specify the folder and file names
    folder_name = f"MedicineNamesCollection/label_{alphabet[index]}"

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for url in range(len(my_label)):
        medicineNamesList = extractMedicineNameFromURL1mg(my_label[url])
        file_name = f"label_{alphabet[index]}_{url+1}.txt"
        # Specify the file path
        file_path = os.path.join(folder_name, file_name)

        # Open the file in write mode
        with open(file_path, 'w') as file:
            # Write each element of the list on a new line
            for item in medicineNamesList:
                file.write(f"{item}\n")

    return f"Done<br>"

def process_label(label):
    maxPage = extractMaxPageNumber(label)
    labelUrlsList = [generate1mgURL(page, label) for page in range(1, maxPage + 1)]
    return labelUrlsList

def extractMedicineNameFromURL1mg(url):

    # proxy = "118.69.111.51:8080"    

    # html = requests.get(url=url,headers=header,proxies={'http' : proxy,'https': proxy})
    html = requests.get(url=url,headers=header)

    soup = BeautifulSoup(html.text, 'html.parser')

    target_divs = soup.find_all('div', class_='style__font-bold___1k9Dl style__font-14px___YZZrf style__flex-row___2AKyf style__space-between___2mbvn style__padding-bottom-5px___2NrDR')

    all_med_name=[]
    if target_divs:
        for div in target_divs:
            inner_div = div.find('div')
            if inner_div:
                extracted_data = inner_div.get_text(strip=True)
                all_med_name.append(extracted_data)
    
    return all_med_name

def generate1mgURL(page_no,label):
    return f"https://www.1mg.com/drugs-all-medicines?page={page_no}&label={label}"

def extractMaxPageNumber(label):

    url = f"https://www.1mg.com/drugs-all-medicines?label={label}"

    html = requests.get(url=url,headers=header)

    soup = BeautifulSoup(html.text, 'html.parser')

    target_links = soup.find_all('a', class_='button-text link-page')

    pageNumbersList = []
    if target_links:
        for link in target_links:
            extracted_data = link.get_text(strip=True)
            pageNumbersList.append(int(extracted_data))
    
    return max(pageNumbersList)
