# coding: utf-8
import requests
import unittest
import time
import re
from bs4 import BeautifulSoup
# from currency_converter import CurrencyConverter
# to use currency_converter make sure to install the package :  pip install --user currencyconverter
# https://pypi.org/project/CurrencyConverter/


website_prefix = "https://www.reuters.com"
reference_currency = "EUR"

number_quarter_tr = 2

def _handle_request_result_and_build_soup(request_result):
    res = requests.get(request_result)
    html_doc = res.text
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup


def _convert_value_to_int(string):
    if "--" in string:
        return 0
    value = float(re.findall("[+-]?\d+\.\d+",string.strip().replace(",",""))[0]) # On ne récupère que les chiffres et le signe
    # To improve later : convert the money to the reference currency indicated
    # to do : use c.currencies to have a set of money, extract the money type and see if its inside
    # c = CurrencyConverter()
    # money_string = reference_currency
    # if "$" in string:
    #     money_string = "USD"
    # if "CHF" in string:
    #     money_string = "CHF"
    # value = c.convert(money_string, reference_currency)
    return value
#
def _convert_percentage_to_int(string):
    if "--" in string:
        return 0
    if "-" in string:
        return -1 * float(string.strip()[2:-2])
    else:
        return float(string.strip()[2:-2])

def _clear_url(string):
    return string.replace("'","").replace("\\","").replace("parent.location=","")

def get_all_links_for_query(query):
    url = website_prefix + "/finance/stocks/lookup?searchType=any&comSortBy=marketcap&sortBy=&dateRange=&search=" +query # plutôt que de passer par une requpête post on apelle directement l'url
    soup = _handle_request_result_and_build_soup(url)

    specific_class = "search-table-data"
    tableContent =soup.find(class_=specific_class).find_all("tr")
    mylinks =[]
    for ind in range (1,len(tableContent)):
        mylinks.append(_clear_url(tableContent[ind].attrs['onclick']))

    return mylinks

def _complete_list_with_0(size,list):
    if (len(list) < size): # we want 4 values
        for i in range (size-len(list)):
            list.append(0)
    return list

def get_last_quarter(soup):
    specific_class = "dataTable"

    table = soup.find(class_= specific_class)

    data_list = table.find_all('tr')[2].find_all('td')
    result_list = []
    for element in data_list[2:]:
        #print("mon element:",element.text)
        result_list.append(_convert_value_to_int(element.text))
    return _complete_list_with_0(4,result_list)

def get_dividend_yield(soup):

    table = soup.find_all(class_='dataTable')
    dividends = table[2].find_all('tr')[1].find_all('td')

    result_list = []
    for element in dividends[1:] :
        result_list.append(_convert_value_to_int(element.text))

    return _complete_list_with_0(3,result_list)


def get_percentage(soup):
    specific_class = "valueContentPercent"
    share_count = soup.find("span", class_= specific_class)
    if (share_count is not None):
        return  _convert_value_to_int(share_count.text)
    else:
        return 0

def get_value(soup):

    specific_class = "valueContent"
    percentage = soup.find("span", class_= "valueContentPercent") # value contains the value & percentage
    share_count = soup.find("span", class_=specific_class)
    if ((percentage is not None) and (share_count is not None)):
        percentage = percentage.text.strip()
        return _convert_value_to_int(share_count.text.replace(percentage, ""))
    else:
        return 0


def get_sharehold(soup):

    table = soup.find_all(class_='dataSmall')
    if len(table)<3:
        # some webpages have not this table
        # example:  https://www.reuters.com/finance/stocks/financial-highlights/AIR.MC
        return 0
    sharehold = table[2].find(class_="data")
    if (sharehold is not None):
        return  _convert_value_to_int(sharehold.text)
    else:
        return 0


def _clear_query(query):
    new_query = re.sub(r'[^\w\s]', '', query.lower()).replace(" ", "+")  # we filter the words from upercase and punctuation and replace space by what we need
    return new_query

def average_column_list(list):
    average = []
    nb_col = len(list[0])
    for i in range (nb_col):
        sum = 0
        for j in range(len(list)):
            sum = sum + list[j][i]
        average.append(sum/len(list))
    return average


def get_popularity_for_company(company):
    start_time = time.process_time()
    query = _clear_query(company)
    list_of_link = get_all_links_for_query(query)
    results_percentage = []
    results_value = []
    results_sharehold = []
    quarter_value = []
    dividend_yield = []
    dict_res = {}
    for url in list_of_link:
        url = url.replace("overview","financial-highlights")
        soup = _handle_request_result_and_build_soup(website_prefix + url)
        #print("link ", url)
        if (soup is not None):
            if (get_percentage(soup) != 0):
                results_percentage.append(get_percentage(soup))
            if (get_value(soup) != 0):
                results_value.append(get_value(soup))
            if (get_sharehold(soup) != 0):
                results_sharehold.append(get_sharehold(soup))
                quarter_value.append(get_last_quarter(soup))
                dividend_yield.append(get_dividend_yield(soup))
    dict_res["list_of_links"] = list_of_link
    dict_res["value"] = results_value
    dict_res["percentage"] = results_percentage
    dict_res["sharehold"] = results_sharehold
    dict_res["nb_links"] = len(list_of_link)
    dict_res["last_quarter"] = quarter_value
    dict_res["dividend_yield"] = dividend_yield
    dict_res["time_compute"] = time.process_time()-start_time
    return dict_res

def average_dictionnary_values(dict_res):
    dict_res["value"] = sum(dict_res["value"]) / len(dict_res["value"])
    dict_res["percentage"] = sum(dict_res["percentage"])/len(dict_res["percentage"])
    dict_res["sharehold"] = sum(dict_res["sharehold"]) / len(dict_res["sharehold"])
    dict_res["last_quarter"] = average_column_list(dict_res["last_quarter"])
    dict_res["dividend_yield"] = average_column_list(dict_res["dividend_yield"])
    return dict_res

def get_dictionnary_link_number(dict_res,link_num):
    dict_res["nb_links"] = 1
    dict_res["list_of_links"] = dict_res["list_of_links"][link_num]
    dict_res["value"] = dict_res["value"][link_num]
    dict_res["percentage"] = dict_res["percentage"][link_num]
    dict_res["sharehold"] = dict_res["sharehold"][link_num]
    dict_res["last_quarter"] = dict_res["last_quarter"][link_num]
    dict_res["dividend_yield"] = dict_res["dividend_yield"][link_num]
    dict_res["time_compute"] = dict_res["time_compute"]
    return dict_res

def print_results(dict, name):

    print("""
    {name} :
    Nombre de liens {nb_links}
    Valeur action {value}
    Pourcentage de variation {percentage}%
    Valeur du dernier trimestre : Moyenne {quarter_mean}, Haute {quarter_high}, Basse {quarter_low}, L'année précédente {quarter_last_year}
    Dividend : Compagnie {dividend_company}, Industrie {dividend_industry}, Secteur {dividend_sector}
    Pourcentage possédé par les investisseurs {sherehold}%
    Temps de calcul {time}s
    """.format(name=name, nb_links=dict["nb_links"], value=dict["value"], percentage=dict["percentage"], quarter_mean=dict["last_quarter"][0], quarter_high=dict["last_quarter"][1],
               quarter_low=dict["last_quarter"][2], quarter_last_year=dict["last_quarter"][3],dividend_sector=dict["dividend_yield"][2],dividend_industry=dict["dividend_yield"][1],
               dividend_company=dict["dividend_yield"][0],sherehold=dict["sharehold"],time=dict["time_compute"]))

    #print(name, " : \n Nombre de liens", dict["nb_links"],"\n Valeur", dict["value"], "\n Pourcentage de variation", dict["percentage"], "\n Temps de calcul", dict["time_compute"],"s")

def scrapper_average_printer(name_list):
    print("""
            Les valeurs présentées ici sont la moyenne de l'indicateur en question de tous les indices de la société. 
            Actuellement c'est la moyenne arithmétique qui est calculée. IL est à noter que la valeur n'est pas 
            toujours exprimée en Euros, il faudrait donc convertir tous les éléments dans la même monaie pour avoir une
            meilleure idée de la qualité de l'investissement.

    """)
    for name in name_list:
        dict = get_popularity_for_company(name)
        dict = average_dictionnary_values(dict)
        print_results(dict,name)

def scrapper_link_number_printer(name_list,number):
    for name in name_list:
        dict = get_popularity_for_company(name)
        dict = get_dictionnary_link_number(dict, number)
        print_results(dict,name)

# In this exercice we will print the full average dictionnary and a slice of it so we make a special method
# not to compute again all the calculations
def scrapper_exercice_printer(name_list,number):
    dict_list = []
    print("***************************************************************************************************")
    print("Values for Paris bourse only : ")
    for name in name_list:
        dict = get_popularity_for_company(name)
        dict_list.append(dict)

    for ind,dict in enumerate(dict_list):
        dict1 = dict.copy()
        dict1 = get_dictionnary_link_number(dict1, number)
        print_results(dict1, name_list[ind])

    print("***************************************************************************************************")
    print("""
            Les valeurs présentées ici sont la moyenne de l'indicateur en question de tous les indices de la société. 
            Actuellement c'est la moyenne arithmétique qui est calculée. IL est à noter que la valeur n'est pas 
            toujours exprimée en Euros, il faudrait donc convertir tous les éléments dans la même monaie pour avoir une
            meilleure idée de la qualité de l'investissement.

    """)
    for ind,dict in enumerate(dict_list):
        dict2 = dict.copy()
        dict2 = average_dictionnary_values(dict2)
        print_results(dict2,name_list[ind])

class Lesson1Tests(unittest.TestCase):

    def testConvertPercentageInt(self):
        self.assertEqual(_convert_percentage_to_int("(+21.64%)"), 21.64)
        self.assertEqual(_convert_percentage_to_int("(-21.64%)"), -21.64)
        self.assertEqual(_convert_percentage_to_int("(--)"), 0)

    def testConvertValueInt(self):
        self.assertEqual(_convert_value_to_int("€21.64"), 21.64)
        self.assertEqual(_convert_value_to_int("€-21.64"), -21.64)
        self.assertEqual(_convert_value_to_int("--"), 0)
        self.assertEqual(_convert_value_to_int("CHF-2.00"), -2.00)
        self.assertEqual(_convert_value_to_int("€142,342.41"), 142342.41)

    def testClearQuery(self):
        self.assertEqual(_clear_query("joe déter a Gàl"), "joe+déter+a+gàl")


print("TESTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")

names_to_test = ["LVMH","Airbus", "Danone"]

scrapper_exercice_printer(names_to_test,0)

def main():
    unittest.main()

if __name__ == '__main__':
    main()





