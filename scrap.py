import requests
from bs4 import BeautifulSoup
import pickle
import time
import sys
import pandas as pd
import os
from PastaMaker import *
import keywords

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
        time.sleep(1)
    return id_dict

def get_soup(id_elite):
    """
    Renvoie une soupe à partir d'un id
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

def tab_to_dic(soup, category = ''):
    
    # On recherche d'abord les headers
    
    header = []
    res = []
    
    for it in soup.find_all('td', attrs = {'class':'b'}):
        if(category != '' and it.text == body):
            if(category == company_association):
                header.append(company_body)
            elif(category == politics):
                header.append(political_body)
            elif(category == sociability):
                header.append(sociability_body)
            else:
                header.append(it.text)
        else:
            header.append(it.text)
    
    if(header != []):
        header_len = len(header)
        i = header_len
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

def get_infos(soup):
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
            infos[functions] += tab_to_dic(tag, tag.find('th').text)
    
    return infos

def unused_keywords(soups):
    res = {}
    res[biography] = []
    res[functions] = []
    res[formation] = []
    ()
    for ID, soup in soups.items():
        infos = get_infos(soup)
        
        if(biography in list(infos.keys())):
            #print("----- BIOGRAPHY -----")
            bio_keywords = list(infos[biography].keys())
            for it in bio_keywords:
                if it not in res[biography] and it not in all_biography_keywords:
                    print(str(ID)+it)
                    res[biography].append(it)
                    
        if(functions in list(infos.keys())):
            #print("----- FUNCTIONS -----")
            for dic in infos[functions]:
                 keys = list(dic.keys())
                 for it in keys:
                     if it not in res[functions] and it not in all_functions_keywords:
                         res[functions].append(it)
                         print(str(ID)+it)
                         
        if(formation in list(infos.keys())):
            #print("----- FUNCTIONS -----")
            for dic in infos[formation]:
                 keys = list(dic.keys())
                 for it in keys:
                     if it not in res[formation] and it not in all_formation_keywords:
                         res[formation].append(it)
                         print(str(ID)+it)
                    
    print(res)