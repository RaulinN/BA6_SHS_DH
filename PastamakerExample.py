import PastaMaker as p
import scrap
import pickle

if __name__ == '__main__':
    pasta = p.PastaMaker("Test.url")
    p_str = {'Données biographiques': {'Nom :': 'Abate',
                                       'Prénom :': 'Fabio',
                                       'Sexe :': 'H',
                                       'Naissance: ': '04.01.1966',
                                       'Lieu naissance :': 'Locarno(TI)'},
             'Formation': [{'année': '(1975)',
                            'titre': 'Licence',
                            'catégorie': 'droit',
                            'lieu': 'UniBe',
                            'pays': 'Suisse'}],
             "Fonctions et mandats": [{'durée': '1499-2000',
                                       'entreprise/association éco': 'Unil',
                                       'fonction': 'Président'}]
             }

    pasta.add_ingredient(p_str)
    pasta.cook()
