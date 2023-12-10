import requests
from bs4 import BeautifulSoup
import random
import concurrent.futures
import MedicineWebScraping
import os
from selenium import webdriver

working_proxy=[]
#Specify the path to the Microsoft Edge WebDriver
edge_driver_path = 'E:/Simentic Search/edgedriver_win64/msedgedriver.exe'
os.environ["PATH"] += os.pathsep + edge_driver_path
# Configure the Edge webdriver
options = webdriver.EdgeOptions()
options.use_chromium = True
options.add_argument("--headless")
def main():
    working_proxy.clear()
    proxylist = getProxies()
    #print(len(proxylist))

    #check them all with futures super quick
    with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(extract, proxylist)
    
    return "<br>".join(working_proxy)

#get the list of free proxies
def getProxies():
    r = requests.get('https://free-proxy-list.net/')
    
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('tbody')

    proxies = []
    for row in table:
        if row.find_all('td')[4].text =='elite proxy':
            proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
            proxies.append(proxy)
        else:
            pass
    
    print(f"Total Proxy: {len(proxies)}")
    return proxies

def extract(proxy):
    #this was for when we took a list into the function, without conc futures.
    #proxy = random.choice(proxylist)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    try:
        #change the url to https://httpbin.org/ip that doesnt block anything
        r = requests.get('https://www.google.com', headers=headers, proxies={'http' : proxy,'https': proxy}, timeout=1)
        working_proxy.append(proxy)
        return proxy
    except requests.ConnectionError as err:
        return ""


