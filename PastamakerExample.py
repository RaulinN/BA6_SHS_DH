import PastaMaker as p
from scrap import *
import pickle

if __name__ == '__main__':
    """

    id = 84917
    id = 94706 # what to do about parethesis
    id= 80060

    id = 56588 # to study more
    #id = 54886
    #id = 63195
    #id = 55435 # good example
    #id = 54885
    #id = 54858
    #id = 61538
    id = 91854
    #id = 59556
    pasta = p.PastaMaker(str(id))
    infos = get_infos(get_soup(id))
    print(infos)
    pasta.add_ingredient(infos)
    pasta.cook()
    """
    # soups = open_var('scrap', 'soups_ID_O_100')
    soups = open_var('scrap', 'soups_ID_A')
    for ID in soups.keys():
        pasta = p.PastaMaker(str(ID)) # Je n'ai mis ici que l'ID pour la visiblité 
        infos = get_infos(soups[ID])
        print("------------------------"+str(ID)+"------------------------")
        print(infos)
        pasta.add_ingredient(infos)
        pasta.cook()
        #"""
