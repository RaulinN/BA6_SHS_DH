from scrap import *
from PastaMaker import *
from QueryManager import *

import time


def main():
    uploadManager: QueryManager = QueryManager()

    """
    Lettres réalisées : A, B, C, D, E, F, G, H, I, X, Y, Z
    R
    

    """

    letters = ['S', 'T', 'U', 'V', 'W']
    print(time.time())

    for letter in letters:
        
        print("----"+letter+"----")
        
        dictionary = get_id(letter.capitalize())
        i, length = 0, len(dictionary.keys())
        

        for eliteId in dictionary.keys():
            try:
                infos = get_infos(get_soup(eliteId), eliteId)
                pasta = PastaMaker(eliteId)
                pasta.add_ingredient(infos)
                pageTitle, payload = pasta.cook()

                uploadManager.uploadInformation(pageTitle.split(" (")[0], str(eliteId), payload)
            except Exception as e:
                print("Unexpected error with eliteId {}".format(eliteId))
                print("Error reason: " + str(e))

            i += 1
            if i % 100 == 0 or i == length or i == 1:
                print(
                    "Progress: {}/{} (Estimated time remaining: {} seconds)".format(i, length, int((length - i) * (3.32 + 0.23)))
                )
                
if __name__ == '__main__':
    main()
