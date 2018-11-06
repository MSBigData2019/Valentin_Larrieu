import re
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#from sklearn import linear_model
#from sklearn.model_selection import train_test_split


SEED=1234

#def split_data(X1,Y1,seed_data):
#    return train_test_split(X1,Y1, test_size=0.2, random_state=seed_data)


def main():
    print("Start")
    # We read the file and prepare the column for the join
    specialiste =  pd.read_excel('C:\\Users\\Orion\\Documents\\MS-BGD\\Git\\Valentin_Larrieu\\Lesson5\\Honoraires_totaux_des_professionnels_de_sante_par_departement_en_2016.xls', sheet_name = "Spécialistes", sep = ",", header = 0).rename(columns={'Spécialistes': 'SPECIALITE'})
    generaliste =  pd.read_excel('C:\\Users\\Orion\\Documents\\MS-BGD\\Git\\Valentin_Larrieu\\Lesson5\\Honoraires_totaux_des_professionnels_de_sante_par_departement_en_2016.xls', sheet_name = "Généralistes et MEP", sep = ",", header = 0).rename(columns={"Généralistes et compétences MEP": 'SPECIALITE'})

    # We join the data
    joined_df = specialiste.append(generaliste)
    #²joined_df = pd.merge(specialiste, generaliste, on='SPECIALITE', left_index=True, right_index=False)
    print(joined_df.shape)
    #print(joined_df.head(50).to_string())

    # We handled non usefull informations
    joined_df = joined_df.replace('nc', np.NaN)
    joined_df['SPECIALITE'] = joined_df['SPECIALITE'].replace(to_replace=r'TOTAL(.*)', value=np.NaN, regex=True)
    joined_df['DEPARTEMENT'] = joined_df['DEPARTEMENT'].replace(to_replace=r'TOTAL(.*)', value=np.NaN, regex=True)
    joined_df = joined_df.dropna(axis=0, how='any')

    print("joined \n",joined_df.shape)
    #print(joined_df.head(50).to_string())

    # We rename the column of our dataframe
    joined_df = joined_df.rename(columns={'HONORAIRES SANS DEPASSEMENT (Euros)': 'HONORAIRES', 'DEPASSEMENTS (Euros)': 'DEPASSEMENTS', 'FRAIS DE DEPLACEMENT (Euros)': 'DEPLACEMENTS','TOTAL DES HONORAIRES (Euros)': 'TOTALHONORAIRES'})
    joined_df['EFFECTIFS'] = pd.to_numeric(joined_df['EFFECTIFS'])
    joined_df['HONORAIRES'] = pd.to_numeric(joined_df['HONORAIRES'])
    joined_df['DEPASSEMENTS'] = pd.to_numeric(joined_df['DEPASSEMENTS'])

    # We separate the id of the department and thee department name (same with speciality)
    joined_df['SPECIALITEID'], joined_df['SPECIALITE'] = joined_df['SPECIALITE'].str.split('- ', 1).str
    joined_df['DEPARTEMENTID'], joined_df['DEPARTEMENT'] = joined_df['DEPARTEMENT'].str.split('- ', 1).str
    joined_df = joined_df.dropna(axis=0, how='any') # Some of our separation may create NA

    # We remove the row where the population is 0
    joined_df = joined_df[joined_df["EFFECTIFS"] > 0]
    print("joined post filter\n", joined_df.shape)
    #print(joined_df.head(100).to_string())
    #print(joined_df.dtypes)


    # We handle the population dataframe
    population =  pd.read_excel('C:\\Users\\Orion\\Documents\\MS-BGD\\Git\\Valentin_Larrieu\\Lesson5\\estim-pop-dep-sexe-gca-1975-2018.xls', sheet_name = "2016", sep = ",", header = None, skiprows = 5)
    population = population.dropna(axis=0, how='any') # Some of our separation may create NA
    population = population.rename(columns={0: 'DEPARTEMENTID', 1: 'DEPARTEMENT', 2: '0/19',3: '20/39',4: '40/59',5: '60/74',6: '75/100',7: 'POPULATION'})
    #print(population.head(100).to_string())
    population_filtered = population[["DEPARTEMENTID","0/19","20/39","40/59","60/74","75/100","POPULATION"]]
    #population_filtered["DEPARTEMENTID"].astype('str')
    #print(population_filtered.head(100).to_string())
    print(population_filtered.dtypes)

    # We join the population dataframe with the previous data
    joined_df_with_pop = pd.merge(joined_df, population_filtered, on='DEPARTEMENTID', left_index=True, right_index=False)

    # We create new features
    joined_df_with_pop["POURCENTAGE_DEPASSEMENT"] = joined_df_with_pop['DEPASSEMENTS'] / (joined_df_with_pop['DEPASSEMENTS'] + joined_df_with_pop['HONORAIRES'])

    joined_df_with_pop["EFFECTIFS/POPULATION"] = joined_df_with_pop['EFFECTIFS'] / joined_df_with_pop['POPULATION']
    print(joined_df_with_pop.head(100).to_string())

    #col_to_select = ['EFFECTIFS', 'HONORAIRES', 'DEPASSEMENTS',"POURCENTAGE_DEPASSEMENT","EFFECTIFS/POPULATION","POPULATION"]
    #dep = joined_df_with_pop.groupby(['DEPARTEMENT'])[col_to_select].sum()
    dep = joined_df_with_pop.groupby(['DEPARTEMENT']).sum()
    #spe = joined_df_with_pop.groupby(['SPECIALITE'])[col_to_select].sum()
    spe = joined_df_with_pop.groupby(['SPECIALITE']).sum()

    #print("test \n", departement)

    # Plot

    #print("DEPARTEMENT")

    #plot_pop_depassement = dep.plot(x='POPULATION', y='POURCENTAGE_DEPASSEMENT', marker='o', color='red', title = "POPULATION as a function of POURCENTAGE_DEPASSEMENT")
    #plt.show()

    #plot_eff_depassement = dep.plot(x='EFFECTIFS', y='POURCENTAGE_DEPASSEMENT', marker='o', color='red', title = "EFFECTIFS as a function of POURCENTAGE_DEPASSEMENT")
    #plt.show()

    #plot_effectif_pop_deplacement = dep.plot(x='EFFECTIFS/POPULATION', y='POURCENTAGE_DEPASSEMENT', marker='o', color='red', title = "EFFECTIFS/POPULATION as a function of POURCENTAGE_DEPASSEMENT")
    #plt.show()

    #print("SPECIALITE")

    # plot_pop_specialite = spe.plot(x='POPULATION', y='POURCENTAGE_DEPASSEMENT', marker='o', color='red', title = "POPULATION as a function of POURCENTAGE_DEPASSEMENT")
    # plt.show()

    # plot_eff_specialite = spe.plot(x='EFFECTIFS', y='POURCENTAGE_DEPASSEMENT', marker='o', color='red', title = "EFFECTIFS as a function of POURCENTAGE_DEPASSEMENT")
    # plt.show()

    # plot_effectif_pop_specialite = spe.plot(x='EFFECTIFS/POPULATION', y='POURCENTAGE_DEPASSEMENT', marker='o', color='red', title = "EFFECTIFS/POPULATION as a function of POURCENTAGE_DEPASSEMENT")
    # plt.show()

    # Regression on data
    """
    X = spe["EFFECTIFS/POPULATION"]
    Y = spe["POURCENTAGE_DEPASSEMENT"]

    X_train, X_test, Y_train, Y_test = split_data(X, Y, SEED)
    skl_lm = linear_model.LinearRegression(fit_intercept=True)
    skl_lm.fit(X_train, Y_train)
    score = skl_lm.score(X_test, Y_test)
    print("Score: \n", score)

    #print("test \n",generaliste)"""
    
    print("end")


if __name__ == "__main__":
	main()
