import spacy
import base64
import binascii

def md7(row_data):
    med7 = spacy.load("en_core_med7_lg")

    # create distinct colours for labels
    # col_dict = {}
    # seven_colours = ['#e6194B', '#3cb44b', '#ffe119', '#ffd8b1', '#f58231', '#f032e6', '#42d4f4']
    # for label, colour in zip(med7.pipe_labels['ner'], seven_colours):
    #     col_dict[label] = colour

    # options = {'ents': med7.pipe_labels['ner'], 'colors':col_dict}
    decoded_bytes = base64.b64decode(row_data)
    decoded_string = decoded_bytes.decode('utf-8')
    doc = med7(decoded_string)

    # spacy.displacy.render(doc, style='ent', jupyter=True, options=options)

    # print(doc.ents)

    # result = [(ent.text, ent.label_) for ent in doc.ents]
    result = {ent.label_: ent.text for ent in doc.ents}
    
    print(result)

    return result
