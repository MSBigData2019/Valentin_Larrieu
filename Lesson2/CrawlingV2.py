# coding: utf-8
import requests
import unittest
import time
import re
from bs4 import BeautifulSoup

website_prefix = "http://www.purepeople.com"

def _handle_request_result_and_build_soup(request_result):
    res = requests.get(request_result)
    html_doc = res.text
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup


def _convert_string_to_int(string):
    if "K" in string:
        string = string.strip()[:-1]
        return float(string.replace(',','.'))*1000
    else:
        return int(string.strip())

def get_all_links_for_query(query):
    number = 0
    url = website_prefix + "/rechercher/q/"
    all_links = []
    more_link = True
    while(more_link):
        number = number + 1
        postUrl = "/cat/article/np/" + str(number)
        res = url + query + postUrl
        soup = _handle_request_result_and_build_soup(res)
        specific_class = "c-article-flux__title"
        my_map = list(map(lambda x : x.attrs['href'] , soup.find_all("a", class_= specific_class)))
        #print("page numéro : ", number)
        if (len(my_map) == 0):
            more_link = False
        all_links = all_links + my_map
    return all_links

def get_share_count_for_page(page_url):
    #res = requests.get(page_url)
    soup = _handle_request_result_and_build_soup(page_url)
    specific_class = "c-sharebox__stats-number"
    share_count_text = soup.find("span", class_= specific_class).text
    return  _convert_string_to_int(share_count_text)

def _clear_query(query):
    new_query = re.sub(r'[^\w\s]', '', query.lower()).replace(" ", "%20")  # we filter the words from upercase and punctuation and replace space by what we need
    return new_query


def get_popularity_for_people(people):
    start_time = time.clock()
    query = _clear_query(people)
    list_of_link = get_all_links_for_query(query)
    results_people = []
    dict_res = {}
    for url in list_of_link:
        results_people.append(get_share_count_for_page(website_prefix + url))
    end_time = time.clock()
    dict_res["share"] = sum(results_people)
    dict_res["nb_links"] = len(list_of_link)
    dict_res["time_compute"] = end_time-start_time
    return dict_res

def print_results(dict, name):
    print(name, " : \n Nombre de liens", dict["nb_links"], "\n Nombre de partages", dict["share"], "\n Temps de calcul", dict["time_compute"],"s")

def scrapper_printer(name_list):
    for name in name_list:
        dict = get_popularity_for_people(name)
        print_results(dict,name)

class Lesson1Tests(unittest.TestCase):
    def testShareCount(self):
        self.assertEqual(get_share_count_for_page("http://www.purepeople.com/article/brigitte-macron-decroche-une-jolie-couv-a-l-etranger_a306389/1") , 172)
        #print("share : ",get_share_count_for_page("http://www.purepeople.com/article/brigitte-macron-decroche-une-jolie-couv-a-l-etranger_a306389/1"))
#
    def testConvertStringInt(self):
        self.assertEqual(_convert_string_to_int("\n                            86\n                    ") , 86)
        self.assertEqual(_convert_string_to_int("5,84K") , 5840)
        self.assertEqual(_convert_string_to_int("\n                            1,6K\n                   ") , 1600)

    def testClearQuery(self):
        self.assertEqual(_clear_query("joe déter a Gàl"), "joe%20déter%20a%20gàl")


names_to_test = ["Poutou","Dupont Aignan", "Marine Le Pen", "Nathalie Arthaud", "Melenchon","Cheminade","Asselineau","Macron","Fillon"]

scrapper_printer(names_to_test)

def main():
    unittest.main()

if __name__ == '__main__':
    main()





