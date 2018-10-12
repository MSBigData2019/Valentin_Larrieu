# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import unittest
import time

website_prefix = "https://www.darty.com"
# List of entries
scrap_list = {
    'Dell': "https://www.darty.com/nav/recherche/dell.html",
    'Acer': "https://www.darty.com/nav/recherche/acer.html",
}

# List collecting the results
results_dic_list = []




def _clear_query(query):
    new_query = re.sub(r'[^\w\s]', '', query.lower()).replace(" ",
                                                              "+")  # we filter the words from upercase and punctuation and replace space by what we need
    return new_query


def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        html_doc = request_result.text
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup


def _convert_value_to_float(string):
    #print("Min string",string)
    if "--" in string:
        return 0
    value = float(
        re.findall("[+-]?\d+\.\d+", string.strip().replace("%", "").replace("-", ""))[0])  # On ne récupère que les chiffres et le signe
    return value


def print_results(dict):
    print("""
    Nom {name} 
    Pourcentage moyen {perc}
    """.format(name=dict["name"],perc=dict["average_pourc"]))


def main():
    print("start")
    for key, value in scrap_list.items():
        #print("loop")
        # Initialization
        data = {'name': key}
        page = requests.get(value)
        soup = BeautifulSoup(page.text, 'html.parser')

        reduc_table = soup.find_all(class_='darty_prix_barre_remise darty_small separator_top')
        #print("table", reduc_table)

        if (reduc_table is not None):
            #print(reduc_table)

            sum = 0
            for pourc in reduc_table:
                sum = sum + _convert_value_to_float(pourc)

            if (len(reduc_table) != 0 ):
                data["average_pourc"] = sum / len(reduc_table)
            else:
                data["average_pourc"] = 0

        else:
            data["average_pourc"] = 0

    # Print of the results
    for dict in results_dic_list:
        print_results(dict)
    if ((results_dic_list[0]["average_pourc"]) > (results_dic_list[1]["average_pourc"])):
        print("dell is the winner !")
    else:
        print("acer is the winner !")


if __name__ == "__main__":
	main()
