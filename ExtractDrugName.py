import json
from drug_named_entity_recognition import find_drugs
from nltk.tokenize import wordpunct_tokenize


def format_response_to_json(response_data):
    formatted_data = []
    for data, _, _ in response_data:
        data['synonyms'] = list(data['synonyms'])  # Convert set to list
        formatted_data.append(data)
    return json.dumps(formatted_data, indent=4)


def find(drug_name):
    tokens = wordpunct_tokenize(drug_name)
    data = find_drugs(tokens, is_ignore_case=True)
    return format_response_to_json(data)