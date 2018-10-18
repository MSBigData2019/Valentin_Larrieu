# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from statistics import mean
import pandas as pd
import json

import unittest
import time

website_prefix = "https://gist.github.com"
website_sufix="/paulmillr/2657075"

# List collecting the results
results_dic_list = []


username = "ValentinLarrieu22"




def main():
    #print("start")
    page = requests.get(website_prefix + website_sufix)
    soup = BeautifulSoup(page.text, 'html.parser')

    # We get the list of usernmes f contributors
    contributor_tr = soup.find("table").findChildren("tr")
    contributors_username = [contributor.find("a").text for contributor in contributor_tr[1:]]


    dict={}

    # We read the token which isstored in a local file
    token = open("/root/Documents/Git_token/gitToken.txt", encoding="utf8") .readline()[:-1]

    for username in contributors_username:
        #print("username",username)
        request = requests.get("https://api.github.com/users/" + username + "/repos", auth=(username, token))

        json_res = json.loads(request.text)

        star_list = [json["stargazers_count"] for json in json_res]
        try:
            dict[username] = mean(star_list)
        except:
            dict[username] = 0

    print(dict)

    #W We convert the dictionnary to a dataframe
    df = {"user": list(dict.keys()), "nb_stars": list(dict.values())}
    df = pd.DataFrame(df)

    # We cast the result
    df["nb_stars"] = df.nb_stars.apply(lambda x: int(x))

    # We print the values we got
    df.sort_values("nb_stars", ascending=False).head(50)




if __name__ == "__main__":
	main()
