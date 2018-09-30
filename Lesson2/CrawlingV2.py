# coding: utf-8
import requests
import unittest
from bs4 import BeautifulSoup

website_prefix = "http://www.purepeople.com"
nb_link = 0
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
    nb_link = len(all_links)
    #print("Nombre de liens : ", len(all_links))

    return all_links

def get_share_count_for_page(page_url):
    #res = requests.get(page_url)
    soup = _handle_request_result_and_build_soup(page_url)
    specific_class = "c-sharebox__stats-number"
    share_count_text = soup.find("span", class_= specific_class).text
    return  _convert_string_to_int(share_count_text)

def get_popularity_for_people(people):
    query = people.replace(" ", "%20")
    list_of_link = get_all_links_for_query(query)
    results_people = []
    for url in list_of_link:
        results_people.append(get_share_count_for_page(website_prefix + url))
    return sum(results_people)


class Lesson1Tests(unittest.TestCase):
    def testShareCount(self):
        #self.assertEqual(get_share_count_for_page("http://www.purepeople.com/article/brigitte-macron-decroche-une-jolie-couv-a-l-etranger_a306389/1") , 86)
        print("share : ",get_share_count_for_page("http://www.purepeople.com/article/brigitte-macron-decroche-une-jolie-couv-a-l-etranger_a306389/1"))

    def testConvertStringInt(self):
        self.assertEqual(_convert_string_to_int("\n                            86\n                    ") , 86)
        self.assertEqual(_convert_string_to_int("5,84K") , 5840)
        self.assertEqual(_convert_string_to_int("\n                            1,6K\n                   ") , 1600)

#dict_macron = get_popularity_for_people('macron')
dict_melenchon = get_popularity_for_people('melenchon')
# dict_daddario = get_popularity_for_people('Alexandra daddario')
# dict_johanson = get_popularity_for_people('Scarlett johansson')
# dict_mitteneare = get_popularity_for_people('Iris mittenaere')

#print("macron : Nombre de liens ", dict_macron )
print("melenchon : ", dict_melenchon)
# print("Alexandra daddario : ", dict_daddario)
# print("scarlett johansson:  ", dict_johanson)
# print("Iris mittenaere : ", dict_mitteneare)

def main():
    unittest.main()

if __name__ == '__main__':
    main()





