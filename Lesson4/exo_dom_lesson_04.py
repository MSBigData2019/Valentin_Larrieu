# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def _give_number_string(string):
    #print("original", string)
    if string is None:
        return 0
    #print("fct 1", string.strip().replace(" ",""))
    #print("fct 2 ", re.findall("[+-]?\d+[\.\d+]?",string.strip().replace(" ","").replace(",","")))
    value = re.findall("[+-]?\d+[\.\d+]?",string.strip().replace(" ","").replace(" ","").replace(",",""))[0] # those spaces are different
    return value


def give_map_text(soup,class_name):
    result_table = soup.find_all(class_= class_name)
    #print("table", result_table)
    return map(lambda x: x.text, result_table)

def give_map_number(soup,class_name):
    result_table = soup.find_all(class_= class_name)
    #print("table", result_table)
    return map(lambda x: int(_give_number_string(x.text)), result_table)

def main():
    print("Start")
    # This list will contain a list of dataframe, one per page scrapped
    df_list = []

    last_page_to_scrap = 5
    # Here we do a for loop in order to choose how many page we scrap (cause its quite long)
    for number in range (1,last_page_to_scrap): # improvement detect how to scrapp all pages not only those
        print("Page number ", number)
        number_page = str(number)

        website = f"https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3AZOE&options=&page={number_page}&regions=FR-PAC%2CFR-IDF%2CFR-NAQ"

        #print("link ", website)
        page = requests.get(website)
        soup = BeautifulSoup(page.text, 'html.parser')

        # We get the data we need from the soup
        list_type_annonce = list(give_map_text(soup, 'txtBlack typeSeller hiddenPhone'))
        list_annee = list(give_map_number(soup, 'fieldYear'))
        list_kilometrage = list(give_map_number(soup, 'fieldMileage'))
        #list_name = list(give_map_text(soup,'version txtGrey7C noBold'))
        list_name = list(map(lambda x: x.find_all("span")[1].text, soup.find_all(class_= 'brandModelTitle')))
        list_price = list(map( lambda y : _give_number_string(y) , map(lambda x: x.find_all("span")[1].text, soup.find_all("nobr"))))

        #set_unique_name = set(list_name)
        #print("set", set(map_name))
        list_argus = []

        # We iterate over our years and name to get the argus value of the car
        for index in range(len(list_name)):
            model_url = list_name[index].replace(" ","+")
            year = list_annee[index]
            argus = f'https://www.lacentrale.fr/cote-auto-renault-zoe-{model_url}-{year}.html'
            #print ("argus ", argus)
            page_argus = requests.get(argus)
            soup_argus = BeautifulSoup(page_argus.text, 'html.parser')
            list_argus_tmp = list(give_map_number(soup_argus, 'jsRefinedQuot'))
            if len(list_argus_tmp) > 0:
                list_argus.append(list_argus_tmp[0])
            else:
                list_argus.append(0)
            #print("MAP argus tmp", list_argus_tmp, "nb elem ", len(list_argus_tmp))

        #print("MAP type", list_type_annonce, "nb elem ", len(list_type_annonce))
        #print("MAP annee", list_annee, "nb elem ", len(list_annee))
        #print("MAP kilometrage", list_kilometrage, "nb elem ", len(list_kilometrage))
        #print("MAP name", list_name, "nb elem ", len(list_name))
        #print("MAP prix", list_price, "nb elem ", len(list_price))
        #print("MAP argus", list_argus, "nb elem ", len(list_argus))

        # We generate our dataframe
        dataframe = pd.DataFrame({"name": list_name, "announce_type": list_type_annonce,  "year": list_annee, "kilometers": list_kilometrage, "price" : list_price, "argus": list_argus})
        #print(dataframe.head(20).to_string())
        df_list.append(dataframe)

    # We concatenate all our dataframes, one per page scraped
    result_dataframe = pd.concat(df_list, ignore_index=True)
    #print("Data Types", result_dataframe.dtypes)
    #print(result_dataframe.head(100).to_string())

    # We filter on the one having an argus positiv, that means the link was found
    posit_argus = result_dataframe['argus'] > 0
    df_with_argus = result_dataframe[posit_argus]
    print(df_with_argus.head(100).to_string())
    print("end")


if __name__ == "__main__":
	main()
