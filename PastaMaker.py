from datetime import datetime
import string
from time import strptime

from keywords import *
from datetime import date
import re

class PastaMaker:

    def __init__(self, url):
        """Create a page"""
        self.url = url
        # Tuples with a date first and then
        self.pages = []
        self.page = []
        self.name = None
        self.lastName = None
        self.error = False

    def __formatName(self):
        if self.lastName is None and self.name is None:
            self.error = True
            return ""
        else:
            text1 = "" if self.name is None else self.name
            space = " " if self.lastName is not None and self.name is not None else ""
            text2 = "" if self.lastName is None else self.lastName
            return text1 + space + text2

    def __endLine(self, date):
        self.__sources()
        self.page.append('\n')
        self.pages.append((date, "".join(self.page)))
        self.page.clear()

    def __startLine(self):
        self.page.append(' * ')

    def __hyperlink(self, word):
        return '[[' + str(word) + ']]'

    def __toWikidate(self, date_str):
        if bool(re.match(r"\d\d.\d\d.\d{4}", date_str)):
            d = datetime.strptime(date_str, "%d.%m.%Y").date()
            return f"{d.year}.{d.month}.{d.day}"
        elif bool(re.match(r"\d{4}", date_str)):
            return re.match(r"\d{4}", date_str).group()
        elif bool(re.match(r"\(\d{4}\)", date_str)):
            return re.match(r"\((\d{4})\)", date_str).group(1)
        else:
            print("Format error with date " + date_str + "+++++++++++++++++++++++++++++")
            return date(1, 1, 1)

    def __todate(self, date_str):
        print("Will date format "+date_str)
        if bool(re.match(r"\d\d.\d\d.\d{4}", date_str)):
            return datetime.strptime(date_str, "%d.%m.%Y").date()
        elif bool(re.match(r"\d{4}", date_str)):
            year = re.match(r"\d{4}", date_str).group()
            return date(int(year), 1, 1)
        elif bool(re.match(r"\(\d{4}\)", date_str)):
            year = re.match(r"\((\d{4})\)", date_str).group(1)
            return date(int(year), 1, 1)
        else:
            print("Format error with date " + date_str + "+++++++++++++++++++++++++++++")
            return date(1, 1, 1)

    def __spaceTime(self, time, space):
        """ First time and then space"""
        time = '-' if time is None else self.__hyperlink(self.__toWikidate(time))
        space = '-' if space is None else self.__hyperlink(space)
        self.page.append(' ' + time + '/' + space + '. ')

    def __sources(self):
        self.page.append('[' + self.url + ']')


    def __biography(self, biography):
        if name in biography:
            self.name = biography[name]

        if first_name in biography:
            self.first_name = biography[first_name]

        if birth in biography and biography[birth]:
            self.__startLine()
            self.__spaceTime(biography[birth],
                             biography[birth_place] if birth_place in biography else None)
            self.page.append(self.__hyperlink("Naissance") + " de " + self.__hyperlink(self.__formatName()))
            self.__endLine(self.__todate(biography[birth]))

        if death in biography and biography[death]:
            self.__startLine()
            self.__spaceTime(biography[death], None)
            self.page.append(self.__hyperlink("Décès") + " de " + self.__hyperlink(self.__formatName()))
            self.__endLine(self.__todate(biography[death]))

    def __formation(self, formations : list):
        for formation in formations:
            formation: dict
            print(formation)
            if year in formation and formation[year]:
                year_str = formation[year]
                print("To be continued ... (#TODO)")





    def add_ingredient(self, ingredient):
        """Add an event to the page"""
        if self.error:
            return
        if biography in ingredient and ingredient[biography]:
            self.__biography(ingredient[biography])

        if formation in ingredient and ingredient[formation]:
            print("Here 2")
            self.__formation(ingredient[formation])

    def cook(self):
        """ Make the past -- I mean returns the page created as a long string"""
        # TODO call the wikipast magic class
        self.pages.sort(key = lambda x: x[0])
        print("".join([x[1] for x in self.pages]))
