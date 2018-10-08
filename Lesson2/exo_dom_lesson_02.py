# coding: utf-8
import requests
import unittest
import time
import re
from bs4 import BeautifulSoup
#from currency_converter import CurrencyConverter
#to use currency_converter make sure to install the package :  pip install --user currencyconverter


website_prefix = "https://www.reuters.com"
reference_currency = "EUR"

def _handle_request_result_and_build_soup(request_result):
    res = requests.get(request_result)
    html_doc = res.text
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup


def _convert_value_to_int(string):
    if "--" in string:
        return 0
    value = float(re.findall("[+-]?\d+\.\d+",string.strip())[0]) # On ne récupère que les chiffres et le signe
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
    number = 0
    url = website_prefix + "/finance/stocks/lookup?searchType=any&comSortBy=marketcap&sortBy=&dateRange=&search=" +query #plutôt que de passer par une requpête post on apelle directement l'url
    soup = _handle_request_result_and_build_soup(url)
    specific_class = "stripe"
    my_map = list(map(lambda x: _clear_url(x.attrs['onclick']), soup.find_all("tr", class_=specific_class)))
    return my_map


    ###
    # all_links = []
    # more_link = True
    # while(more_link):
    #     number = number + 1
    #     postUrl = "/cat/article/np/" + str(number)
    #     res = url + query + postUrl
    #     soup = _handle_request_result_and_build_soup(res)
    #     specific_class = "c-article-flux__title"
    #     my_map = list(map(lambda x : x.attrs['href'] , soup.find_all("a", class_= specific_class)))
    #     #print("page numéro : ", number)
    #     if (len(my_map) == 0):
    #         more_link = False
    #     all_links = all_links + my_map
    # return all_links

def get_percentage(soup):
    #res = requests.get(page_url)
    #soup = _handle_request_result_and_build_soup(page_url)
    specific_class = "valueContentPercent"
    share_count = soup.find("span", class_= specific_class)
    if (share_count is not None):
        return  _convert_value_to_int(share_count.text)
    else:
        return 0

def get_value(soup):
    #res = requests.get(page_url)
    #soup = _handle_request_result_and_build_soup(page_url)
    specific_class = "valueContent"
    percentage = soup.find("span", class_= "valueContentPercent")# value contains the value & percentage
    share_count = soup.find("span", class_=specific_class)
    if ((percentage is not None) and (share_count is not None)):
        percentage = percentage.text.strip()
        return _convert_value_to_int(share_count.text.replace(percentage, ""))
    else:
        return 0


def _clear_query(query):
    new_query = re.sub(r'[^\w\s]', '', query.lower()).replace(" ", "+")  # we filter the words from upercase and punctuation and replace space by what we need
    return new_query


def get_popularity_for_company(company):
    start_time = time.clock()
    query = _clear_query(company)
    list_of_link = get_all_links_for_query(query)
    results_percentage = []
    results_value = []
    dict_res = {}
    for url in list_of_link:
        soup = _handle_request_result_and_build_soup(website_prefix + url)
        if (soup is not None):
            results_percentage.append(get_percentage(soup))
            results_value.append(get_value(soup))
    end_time = time.clock()
    #dict_res["share"] = 0
    dict_res["value"] = sum(results_value) / len(results_value)
    dict_res["percentage"] = sum(results_percentage)/len(results_percentage)
    dict_res["nb_links"] = len(list_of_link)
    dict_res["time_compute"] = end_time-start_time
    return dict_res

def print_results(dict, name):
    print(name, " : \n Nombre de liens", dict["nb_links"],"\n Valeur", dict["value"], "\n Pourcentage de variation", dict["percentage"], "\n Temps de calcul", dict["time_compute"],"s")

def scrapper_printer(name_list):
    for name in name_list:
        dict = get_popularity_for_company(name)
        print_results(dict,name)

class Lesson1Tests(unittest.TestCase):
    # def testShareCount(self):
    #     self.assertEqual(get_share_count_for_page("http://www.purepeople.com/article/brigitte-macron-decroche-une-jolie-couv-a-l-etranger_a306389/1") , 172)
    #
    def testConvertPercentageInt(self):
        self.assertEqual(_convert_percentage_to_int("(+21.64%)"), 21.64)
        self.assertEqual(_convert_percentage_to_int("(-21.64%)"), -21.64)
        self.assertEqual(_convert_percentage_to_int("(--)"), 0)

    def testConvertValueInt(self):
        self.assertEqual(_convert_value_to_int("€21.64"), 21.64)
        self.assertEqual(_convert_value_to_int("€-21.64"), -21.64)
        self.assertEqual(_convert_value_to_int("--"), 0)
        self.assertEqual(_convert_value_to_int("CHF-2.00"), -2.00)

    def testClearQuery(self):
        self.assertEqual(_clear_query("joe déter a Gàl"), "joe+déter+a+gàl")

    # def testClearUrl(self):
    #     self.assertEqual(_clear_query('parent.location=\'/finance/stocks/overview?symbol=AIRG.HA\''), "finance/stocks/overview?symbol=AIRG.HA")


names_to_test = ["LVMH","Airbus", "Danone"]

scrapper_printer(names_to_test)

def main():
    unittest.main()

if __name__ == '__main__':
    main()





