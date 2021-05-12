import PastaMaker as p
from scrap import *
import pickle

if __name__ == '__main__':
    soups = open_var('scrap', 'soups_ID_A')   
    for ID in soups.keys():
        pasta = p.PastaMaker(str(ID)) # Je n'ai mis ici que l'ID pour la visiblité 
        infos = get_infos(soups[ID])
        print("------------------------"+str(ID)+"------------------------")
        pasta.add_ingredient(infos)
        pasta.cook()
