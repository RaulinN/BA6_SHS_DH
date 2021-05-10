import requests
from bs4 import BeautifulSoup
import pickle
import time
import sys
import pandas as pd
import os
from PastaMaker import *

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

def tab_to_df_dic(soup, given_header = []):
    """
    Prends une soupe tableau qui ne comporte qu'un header, plusieurs sous tableaux <th> possibles
    Ressort un dictionnaire avec en clé le nom du sous tableau (<th>) et un dataframe correspondant au sous-tableau en valeur
    
    Il est possible de notifier les headers lorsqu'ils n'existent pas : si aucun header n'est reconnu, renvoie {'Error':'Error'}
    
    Problème constaté avec les headers, dans le doute je mets toujours []
    """
    storage = {}
    
    header = given_header
    
    if(header == []):
        # On recherche d'abord le header
        for tag in soup.find_all('td', attrs = {'class' : 'b'}):
            header.append(tag.text)
            
    header_len = len(header)
        
    # Si jamais les en-têtes ne sont pas trouvées ou informées, on ne sait pas combien il y a de colonnes
    # On stop le scrap pour la formation
        
    if(header_len != 0):
        # Pour chacun des sous-tableaux, on crée un df que l'on viens remplir
            
        current_tab_name = ''
        current_row = {}
        i = 0
        
        for tag in soup.find_all({'td', 'th'}, attrs = {'class' : ''}):
            if(tag.name == 'th'):
                current_tab_name = tag.text
                storage[current_tab_name] = pd.DataFrame(columns = header)
                continue
            if(current_tab_name == ''):
                current_tab_name = 'Default'
                storage[current_tab_name] = pd.DataFrame(columns = header)
            if(i < header_len - 1):
                current_row[header[i]] = tag.text
                i += 1
            elif(i == header_len - 1):
                current_row[header[i]] = tag.text
                
                # On vérifie si c'est une ligne vide
                for values in current_row.values():
                    if values != '':
                        storage[current_tab_name] = storage[current_tab_name].append(current_row, ignore_index = True)
                        break
                i = 0
    else:
        storage = {'Error':'Error'}
        
    header = []
        
    return storage

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
        infos['Données Biographie'] = tab_to_df_dic(soup_bio, ['field','value'])[soup_bio.find('th').text]
    
    # Formation, tableau
    
    soup_forma = soup.find('table', attrs = {'class' : 'form'})
    
    if(soup_forma is not None):
        
        infos['Formation'] = tab_to_df_dic(soup_forma)

    # Fonctions et mandats
    
    soup_fonc = soup.find_all('table', attrs = {'class' : 'fem'})
    
    
    if(len(list(soup_fonc)) > 0):
        
        infos['Fonctions et mandats'] = {}
        
        for tag in soup_fonc:
            infos['Fonctions et mandats'] = {**infos['Fonctions et mandats'], **tab_to_df_dic(tag, [])}
            
    # Militaire
    """
    soup_mili = soup.find('table', attrs = {'class' : 'emg'})
    
    if(soup_mili is not None):
        infos['Militaire'] = tab_to_df_dic(soup_mili, ['field','value'])['Default']
    """    
    # Ajout de l'ID
    
    infos['ID'] = id_elite
        
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
"""
{'BIOGRAPHY':
     {'BIRTH_DATE':'...'}
 'FORMATION':
     [{'année' : ..., }, ...],
 'FONCTIONS': 
     [{'année' : ..., }, ...]
}
"""


def get_infos(id_elite, soup):
    
    # Résultat 
    
    infos = {}

    # Données biographiques
    
    soup_bio = soup.find('table', attrs = {'class' : 'bio'})
    
    if(soup_bio is not None):
        infos[biography] = bio_tab_reader(soup_bio)[0]
    
    # Ajout de l'ID
    
    infos['ID'] = id_elite
        
    return infos

def bio_tab_reader(soup):
            
    key = ''
    key_state = False
    res = {}
    new_keys = []
    
    for tag in soup.find_all({'td'}, attrs = {'class' : ''}):
        
        text = tag.text
        
        if(key_state):
            key_state = False
            if(key == bio_tab[3]):
                dates = text.split()
                key2 = ''
                key2_state = False
                for it in dates:
                    if(key2_state):
                        if(key2 in bio_tab):
                            res[key2] = it
                        else:
                            key_state.append(key2)
                        key2_state = False
                    else:
                        key2_state = True
                        key2 = it
                        
            elif(key in bio_tab):
                res[key] = text
            else:
                new_keys.append(key)
            key_state = False
        else:
            key = text
            key_state = True
            
    return [res, new_keys]

def tab_reader(soup):
    