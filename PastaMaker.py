from datetime import datetime
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
        # true is female, false is male
        self.sex = None

    def __sources(self):
        self.page.append(' [' + self.url + ']')

    def __startLine(self):
        self.page.append(' * ')

    def __endLine(self, date):
        self.__sources()
        self.page.append('\n')
        self.pages.append((date, "".join(self.page)))
        self.page.clear()

    def __hyperlink(self, word):
        """Returns a string with word as hyperlink
        :rtype: str
        """
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

    def __spaceTime(self, time, space):
        """ First time and then space"""
        time = '-' if time is None else self.__hyperlink(self.__toWikidate(time))
        space = '-' if space is None else self.__hyperlink(space)
        self.page.append(' ' + time + ' / ' + space + '. ')

    def __formatName(self):
        if self.lastName is None and self.name is None:
            print("Impossible to format name with no first or last name given +++++++++++++++++++++++++++++")
            return ""
        else:
            text1 = "" if self.name is None else self.name
            space = " " if self.lastName is not None and self.name is not None else ""
            text2 = "" if self.lastName is None else self.lastName
            #print(self.name, self.lastName)
            return text1 + space + text2

    def __todate(self, date_str):
        #print("Will date format " + date_str)
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

    def __if_sex(self, none, female, male):
        if self.sex is None:
            return none
        elif self.sex:
            return female
        else:
            return male

    def __biography(self, biography):
        if sex in biography:
            biography[sex]: str
            self.sex = False if biography[sex].upper() == 'H' else True

        if name in biography:
            self.name = biography[first_name]

        if first_name in biography:
            self.lastName = biography[name]

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

    def __formation(self, formations: list):
        for formation in formations:
            formation: dict
            if year in formation and formation[year]:
                self.__startLine()
                self.__spaceTime(formation[year], None)
                sex_diplome = self.__if_sex("diplomé(e)", "diplomée", "diplomé")
                self.page.append(self.__hyperlink("Diplôme") + ': ' +
                                 self.__hyperlink(self.__formatName()) + ' ' + sex_diplome)

                if place in formation and formation[place]:
                    self.page.append(" de " + self.__hyperlink(formation[place]))
                if title in formation and formation[title]:
                    self.page.append(" : " + formation[title])
                    if category in formation and formation[category]:
                        self.page.append(" en " + formation[category])

                self.__endLine(self.__todate(formation[year]))

    def __functions(self, functions_dict: list):
        for fun in functions_dict:
            fun: dict
            if duration in fun and fun[duration] and function in fun and fun[function]:
                self.__startLine()
                self.__spaceTime(fun[duration], None)
                self.page.append(self.__hyperlink(self.__formatName()) + " est " + fun[function])
                if company in fun and fun[company]:
                    self.page.append(" de " + self.__hyperlink(fun[company]))
                self.__endLine(self.__todate(fun[duration]))

    def add_ingredient(self, ingredient):
        """Add an event to the page"""
        if biography in ingredient and ingredient[biography]:
            self.__biography(ingredient[biography])

        if formation in ingredient and ingredient[formation]:
            self.__formation(ingredient[formation])

        if functions in ingredient and ingredient[functions]:
            self.__functions(ingredient[functions])

    def cook(self):
        """ Make the past -- I mean returns the page created as a long string"""
        # TODO call the wikipast magic class
        self.pages.sort(key=lambda x: x[0])
        payload = "".join([x[1] for x in self.pages])
        print(payload)
