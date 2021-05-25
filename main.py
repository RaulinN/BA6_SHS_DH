from scrap import *
from PastaMaker import *
from QueryManager import *

import time


def main():
    uploadManager: QueryManager = QueryManager()

    # soups = open_var('scrap', 'soups_ID_Z')

    letters = ['Y']
    print(time.time())

    for letter in letters:
        dictionary = get_id(letter.capitalize())
        i, length = 0, len(dictionary.keys())

        for eliteId in dictionary.keys():
            try:
                infos = get_infos(get_soup(dictionary[eliteId]), eliteId)

                pasta = PastaMaker(eliteId)
                pasta.add_ingredient(infos)
                pageTitle, payload = pasta.cook()

                # uploadManager.uploadInformation(pageTitle.split(" (")[0], str(eliteId), payload)
            except:
                print("Unexpected error with eliteId {}".format(eliteId))
                print()

            i += 1
            if i % 100 == 0 or i == length:
                print(
                    "Progress: {}/{} (Estimated time remaining: {} seconds)".format(i, length, int((length - i) * (3.32 + 0.23)))
                )

    print(time.time())


if __name__ == '__main__':
    main()
