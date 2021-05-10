import requests
from bs4 import BeautifulSoup
import pickle
import time
import sys
import pandas as pd
import os
from PastaMaker import *
import keywords

# CATEGORIES
biography = "Données biographiques"
formation = "Formation"
functions = "Fonctions et mandats"

# BIOGRAPHY
name = "Nom :"
first_name = "Prénom :"
sex = "Sexe :"
dates = "Dates :"
birth = "Naissance:"
death = "Décès:"
birth_place = "Lieu naissance :"

# FORMATION
year = "année"
title = "titre"
category = "catégorie"
place = "lieu"
country = "pays"

# FUNCTIONS
duration = "durée"
company = "entreprise/association éco"
function = "fonction"
company_body = "organe" 

bio_tab = [name, first_name, sex, dates, birth, death, birth_place]

def get_id(letter, existing_elites=[], limit = 100000):
    """
    Prends en entrée la lettre du début du nom des élites que l'on souhaite extraire 
    et un tableau des élites déjà existantes sous la format [Nom, Prénom]
    Renvoie un dictionnaire dont la clé est l'ID URL de l'élite et la valeur est un tableau [Nom, Prénom]
    """
    
    id_dict = {}
    url = "https://www2.unil.ch/elitessuisses/index.php?page=indexPersonnes&alpha=" + letter
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib').find(id='contleft').find('table').find_all(attrs={"bgcolor" : ["#D6E1EC", "#94D2E1"]})
    i = 1
    tot = str(min(len(list(soup)), limit))
    
    for tag in soup:
        if(i > limit):
            break
        tag_a = tag.find_all('a')
        identity = [tag_a[0].text, tag_a[1].text]
        elite_id = int(tag_a[0]['href'][38:])
        
        if(identity not in existing_elites):
            id_dict[elite_id] = identity
        print(str(i)+"/"+tot)
        i += 1
    return id_dict

def get_soup(id_elite):
    """
    Renvoie une soupe à partir d'un id'
    """

    url = 'https://www2.unil.ch/elitessuisses/index.php?page=detailPerso&idIdentite='+str(id_elite)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    return soup.find(id='contleft')

def save_var(variable, directory, name):
    """
    Sauvegarde la variable variable dans directory dans un fichier name.pickle
    """
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    path = directory + '/' + name + '.pickle'

    with open(path, 'wb') as f:
        pickle.dump(variable, f)
    
    print("Sauvegarde réussie")
        
def open_var(directory, name):
    """
    Retourne la variable stockée dans le fichier name.pickle dans le directory
    """
    with open(directory + '/' + name + '.pickle', "rb") as f:
        print("Ouverture réussie")
        return pickle.load(f)

def tab_to_dic(soup):
    
    # On recherche d'abord les headers
    
    header = []
    
    for it in soup.find_all('td', attrs = {'class':'b'}):
        header.append(it.text)
        
    if(header != []):
        header_len = len(header)
        i = header_len
        res = []
        temp_dic = {}
        for it in soup.find_all('td', attrs = {'class':''}):
            if(it.text != ''):
                temp_dic[header[i%header_len]]= it.text
            if(i%header_len == header_len - 1):
                if(temp_dic != {}):
                    res.append(temp_dic)
                temp_dic = {}
            i += 1            
                
    return res

def get_infos(id_elite, soup):
    
    """
    Renvoie les informations sous la forme d'un dictionnaire d'une élite donnée (on donne un ID et la soupe correspondante)
    
    Le dictionnaire se présente sous la forme (lorsque les catégories existent): 
    {'ID' : l'ID renseigné en argument
     'Données Biographie' : Dataframe des données biographiques,
     'Militaire' : Dataframe des données biographiques,
     'Fonctions et mandats' : {
         {Catégorie 1} : Dataframe de la catégorie
         {Catégorie 2} : Dataframe de la catégorie 
         ...
         },
     'Formation' : {
         {Catégorie 1} : Dataframe de la catégorie
         {Catégorie 2} : Dataframe de la catégorie 
         ...
         },
     }
    """
    # Résultat 
    
    infos = {}

    # Données biographiques
    
    soup_bio = soup.find('table', attrs = {'class' : 'bio'})
    
    if(soup_bio is not None):
        key_catch = ''
        infos[biography] = {}
        
        for it in soup_bio.find_all('td'):
            if(key_catch != ''):
                infos[biography][key_catch] = it.text
                key_catch = ''
            elif(it.text != ''):
                key_catch = it.text
        
        if dates in infos[biography].keys():
            data = infos[biography][dates].split()
            key_catch = ''
            for i in range(len(data)):
                if(i%2):
                    infos[biography][key_catch] = data[i]
                    key_catch = ''
                else:
                    key_catch = data[i]
                i += 1
            del infos[biography][dates]
    
    # Formation, tableau
    
    soup_forma = soup.find('table', attrs = {'class' : 'form'})
    
    if(soup_forma is not None):
        
        infos[formation] = tab_to_dic(soup_forma)
        
    
    # Fonctions et mandats
    
    soup_fonc = soup.find_all('table', attrs = {'class' : 'fem'})
    
    
    if(len(list(soup_fonc)) > 0):
        
        infos[functions] = []
        
        for tag in soup_fonc:
            infos[functions] += tab_to_dic(tag)
   
    # Ajout de l'ID
    
    infos[identificator] = id_elite
    
    return infos

# Executions

# Importation/Scrap des ID 
#save_var(get_id('O', limit = 100), 'scrap', 'ID_O_100')
#ID_O_100 = open_var('scrap', 'ID_O_100')

# Importation/Scrap des soups
"""
soups_ID_O_100 = {}
i = 1
l = str(len(ID_O_100.keys()))
for ID in ID_O_100.keys():
    start = time.time()
    soups_ID_O_100[ID] = get_soup(ID)
    print(str(i)+"/"+l+' Temps : '+str(time.time() - start))
    i += 1
    time.sleep(1)
    
save_var(soups_ID_O_100, 'scrap', 'soups_ID_O_100')
"""
soups_ID_O_100 = open_var('scrap', 'soups_ID_O_100')

# Détermination des infos => dico
"""
infos_ID_O_100 = {}
i = 1
l = str(len(ID_O_100.keys()))
for ID,soup in soups_ID_O_100.items():
    start = time.time()
    infos_ID_O_100[ID] = get_infos(ID, soup)
    print(str(i)+"/"+l+' Temps : '+str(time.time() - start))
    i += 1
save_var(infos_ID_O_100, 'scrap', 'infos_ID_O_100')
"""
#infos_ID_O_100 = open_var('scrap', 'infos_ID_O_100')

print(get_infos(55409, soups_ID_O_100[55409]))
