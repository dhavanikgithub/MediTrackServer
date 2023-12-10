import requests
from bs4 import BeautifulSoup

def startProgram():
    urls = ["https://www.orpha.net/consor/cgi-bin/Disease_Search_List.php?lng=EN&TAG=0"]
    for i in range(65, 91):
        newitem = "https://www.orpha.net/consor/cgi-bin/Disease_Search_List.php?lng=EN&TAG="+chr(i)
        urls.append(newitem)


    # Function to extract data from the URLs
    def extract_data_from_url(url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            result_box = soup.find('div', {'id': 'result-box'})
            if result_box:
                return result_box.text
            else:
                return f"No data found for {url}"
        else:
            return f"Failed to fetch data from {url}"

    # Function to write data to a text file
    def write_to_text_file(data, file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data)

    data = extract_data_from_url(urls[0])
    file_path = f"DiseaseName/data_0_9.txt"
    write_to_text_file(data, file_path)
    removeEmptyLine(file_path)

    # Extract data from each URL and store it in a text file
    for i in range(1,len(urls)):
        data = extract_data_from_url(urls[i])
        file_path = f"DiseaseName/data_{chr(i+64)}.txt"
        write_to_text_file(data, file_path)
        removeEmptyLine(file_path)
    
    return "Data saved to DiseaseName folder"

def removeEmptyLine(file_path):
    # Read the file and remove empty lines
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        file.seek(0)  # Move the cursor to the beginning of the file
        file.writelines(line for line in lines if line.strip())
        file.truncate()  # If the new content is smaller than the old content, truncate the remaining part
