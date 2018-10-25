# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json


prefix = "https://www.open-medicaments.fr/"

def _give_number_string(string):
    #print("original", string)
    if string is None:
        return 0
    #print("fct 1", string.strip().replace(" ",""))
    #print("fct 2 ", re.findall("[+-]?\d+[\.\d+]?",string.strip().replace(" ","").replace(",","")))
    value = re.findall("[+-]?\d+[\.\d+]?",string.strip().replace("\\xa","").replace(" ","").replace(" ","").replace(",",""))[0] # those spaces are different
    return value


def give_map_text(soup,class_name):
    result_table = soup.find_all(class_= class_name)
    #print("table", result_table)
    return map(lambda x: x.text, result_table)

def give_map_number(soup,class_name):
    result_table = soup.find_all(class_= class_name)
    #print("table", result_table)
    return map(lambda x: int(_give_number_string(x.text)), result_table)

def _handle_request_result_and_build_soup(request_result):
  if request_result.status_code == 200:
    html_doc =  request_result.text
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup

def get_type(label):
    splited = label.split(",")
    #print("splited",splited)
    return splited[1]

def main():
    print("Start")
    # This list will contain a list of dataframe, one per page scrapped
    df_list = []
    page = requests.get(prefix)
    soup = BeautifulSoup(page.text, 'html.parser')
    #print("soup ", soup)

    #on utilise une api
    api_adress = "https://www.open-medicaments.fr/api/v1/medicaments?limit=100&query=paracetamol"
    request = requests.get(api_adress)
    json_res = json.loads(request.text)
    print("json",json_res)
    list_col = ["Quantite","Prix","Laboratoire","Compostion"]
    list_denomi = [json1["denomination"] for json1 in json_res]
    list_code = [json1["codeCIS"] for json1 in json_res]
    list_type = list(map(lambda x: get_type(x), list_denomi))

    print("list type", list_type)
    #print("denom", list_denomi)
    dataframe = pd.DataFrame({"codeCIS": list_code, "denomination": list_denomi, "type":list_type})


    #print(dataframe.head(100).to_string())
    print("end")


if __name__ == "__main__":
	main()
