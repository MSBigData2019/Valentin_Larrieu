
import requests
from statistics import mean
import pandas as pd
import json


website_prefix = "http://fr.distance24.org/route.json?stops="

# List collecting the results
results_dic_list = []





def main():

    #TO DO get the list of 50 bigest cities in france
    list_cities = ["Paris","Marseille","Lyon"]
    list_cities2 = ["Paris","Marseille","Lyon"]
    cities_dataframe = pd.DataFrame(list_cities,list_cities2)

    cities_dataframe.crosstab("city1", "city2")
    # Create a dataframe of all the combination of lines and columns

    # We go through each combination
    for city1 in list_cities:
        for city2 in list_cities2:
            request = requests.get("http://fr.distance24.org/route.json?stops=" + city1 + "|", city2)
            result = json(request)
            #get the distance
            cities_dataframe.loc[cities_dataframe.city1 == city1,["city2"]] = result

    # We cast the result
    cities_dataframe = cities_dataframe.apply(lambda x: int(x))

    # We print the values we got
    print(cities_dataframe.head(50).to_string())




if __name__ == "__main__":
	main()
