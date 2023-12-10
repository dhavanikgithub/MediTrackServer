from flask import Flask, request
import SemanticSearchParallel
import MedicineWebScraping
import concurrent.futures
import ExtractDrugName
import json
import ExtractDiseaseNameList
import get_api_data
import base64
import requests
import CorrectSpelling
import re
import my_testing
import CollectMedicineNameData
import scrapeproxies
import SemanticSearchSequential
import NER

app = Flask(__name__)

@app.route("/collect_medicine",methods=['GET','POST','PUT','DELETE','PATCH','HEAD','OPTIONS','PROPFIND','CUSTOM'])
def doCollect():
    if request.method != 'GET':
        return {"error":"Not valid request. Only accept GET request"}
    return CollectMedicineNameData.main()

@app.route("/label_data/<string:row_data>",methods=['GET','POST','PUT','DELETE','PATCH','HEAD','OPTIONS','PROPFIND','CUSTOM'])
def labelData(row_data):
    if request.method != 'GET':
        return {"error":"Not valid request. Only accept GET request"}
    return NER.md7(row_data)

@app.route("/extract_drugs_name/<string:drug_name_query>",methods=['GET','POST','PUT','DELETE','PATCH','HEAD','OPTIONS','PROPFIND','CUSTOM'])
def findDrugName(drug_name_query):
    if request.method != 'GET':
        return {"error":"Not valid request. Only accept GET request"}
    response = ExtractDrugName.find(drug_name_query)
    return json.loads(response)

@app.route("/spell_correct/<string:query>",methods=['GET','POST','PUT','DELETE','PATCH','HEAD','OPTIONS','PROPFIND','CUSTOM'])
def spellCheck(query):
    if request.method != 'GET':
        return {"error":"Not valid request. Only accept GET request"}
    return {"success":CorrectSpelling.main(query)}
    

@app.route("/test",methods=['GET','POST','PUT','DELETE','PATCH','HEAD','OPTIONS','PROPFIND','CUSTOM'])
def mytest():
    if request.method != 'GET':
        return {"error":"Not valid request. Only accept GET request"}
    # url = f"https://www.google.com/search?q={query}+medicine+used+for%3F&oq={query}+medicine+used+for%3F"
    url = f"https://www.1mg.com/drugs-all-medicines?page=1&label=a"
    return my_testing.start_my_process(url)


@app.route("/",methods=['GET','POST','PUT','DELETE','PATCH','HEAD','OPTIONS','PROPFIND','CUSTOM'])
def home():
    if request.method != 'GET':
        return {"error":"Not valid request. Only accept GET request"}
    # return ExtractDiseaseNameList.startProgram()
    # return "Home"
    # return scrapeproxies.main()
    #return get_api_data.get_user_data()
    return my_testing.index()


@app.route("/medicine_web_scrap/<string:medicine_name_query>",methods=['GET','POST','PUT','DELETE','PATCH','HEAD','OPTIONS','PROPFIND','CUSTOM'])
def medInfoData(medicine_name_query):
    if request.method != 'GET':
        return {"error":"Not valid request. Only accept GET request"}
    if medicine_name_query=="":
        return {"warning":"Please Enter Medicine Name"}
    
    return MedicineWebScraping.main(medicine_name_query)
    

@app.route("/<string:query>",methods=['GET','POST','PUT','DELETE','PATCH','HEAD','OPTIONS','PROPFIND','CUSTOM'])
def query_function(query):
    if request.method != 'GET':
        return {"error":"Not valid request. Only accept GET request"}
    res = SemanticSearchParallel.find(query)
    return res


def run_flask():
    app.run(host='0.0.0.0', port=3000, debug=True)

if __name__ == "__main__":
    run_flask()