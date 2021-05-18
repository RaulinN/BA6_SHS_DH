from datetime import datetime
from keywords import *
from datetime import date
import re


class PastaMaker:
    annoying_chars = ' ≤>≥?-'

    def __init__(self, id: int):
        """Create a page"""
        self.id = str(id)
        self.url = 'https://www2.unil.ch/elitessuisses/index.php?page=detailPerso&idIdentite=' + str(id)
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
        return '[[' + str(word).strip(' ?') + ']]'

    def __toWikidate(self, date_str: str):
        date_str = date_str.lstrip(self.annoying_chars)
        if bool(re.match(r"\d\d?\.00\.\d{4}", date_str)):
            return date(1, 1, 1)
        elif bool(re.match(r"00\.\d\d?\.\d{4}", date_str)):
            return date(1, 1, 1)
        elif bool(re.match(r"\d\d?\.\d\d?\.\d{4}", date_str)):
            d = datetime.strptime(date_str, "%d.%m.%Y").date()
            return f"{d.year}.{d.month}.{d.day}"
        elif bool(re.match(r"\d\d?/\d\d?/\d{4}", date_str)):
            d = datetime.strptime(date_str, "%d/%m/%Y").date()
            return f"{d.year}.{d.month}.{d.day}"
        elif bool(re.match(r"\d{4}", date_str)):
            return re.match(r"\d{4}", date_str).group()
        elif bool(re.match(r"\(\d{4}\)", date_str)):
            return re.match(r"\((\d{4})\)", date_str).group(1)
        else:
            print("Format error with date " + date_str +'=='+ date_str.lstrip(' ') + '@' + self.url + "+++++++++++++++++++++++++++++")
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
            return text1 + space + text2 +  ' (' + self.id + ')'

    def __parethisisOff(self, words):
        return re.match(r"([^\(]+)(\(.+\))?", words).groups()

    def __todate(self, date_str):
        date_str = date_str.lstrip(self.annoying_chars)
        #print("Will date format " + date_str)
        if bool(re.match(r"\d\d?\.00\.\d{4}", date_str)):
            return date(1, 1, 1)
        elif bool(re.match(r"00\.\d\d?\.\d{4}", date_str)):
            return date(1, 1, 1)
        elif bool(re.match(r"\d\d?\.\d\d?\.\d{4}", date_str)):
            return datetime.strptime(date_str, "%d.%m.%Y").date()
        elif bool(re.match(r"\d\d?/\d\d?/\d{4}", date_str)):
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        elif bool(re.match(r"\d{4}", date_str)):
            year = re.match(r"\d{4}", date_str).group()
            return date(int(year), 1, 1)
        elif bool(re.match(r"\(\d{4}\)", date_str)):
            year = re.match(r"\((\d{4})\)", date_str).group(1)
            return date(int(year), 1, 1)
        else:
            print("Format error with date " + date_str + '@' + self.url + "+++++++++++++++++++++++++++++")
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
            if year in formation and formation[year].lstrip(self.annoying_chars):
                self.__startLine()
                self.__spaceTime(formation[year],
                                 formation[country] if country in formation else None)
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
            if duration in fun and fun[duration].lstrip(self.annoying_chars) and fun[duration] != 'CONFIDENTIEL' and function in fun and fun[
                function]:
                self.__startLine()
                self.__spaceTime(fun[duration], None)

                self.page.append(self.__hyperlink(self.__formatName()) + " est " + fun[function].strip(' ?'))

                if university in fun and fun[university]:
                    groups = self.__parethisisOff(fun[university])
                    if groups[0] is not None:
                        arg = '' if groups[1] is None else ' ' + groups[1]
                        self.page.append(" à " + self.__hyperlink(groups[0]) + arg)

                if company in fun and fun[company]:
                    self.page.append(" de " + self.__hyperlink(fun[company]))

                if political_party in fun and fun[political_party]:
                    self.page.append(" du/des " + self.__hyperlink(fun[political_party]))

                if entity in fun and fun[entity]:
                    self.page.append(" dans le/la " + self.__hyperlink(fun[entity]))

                if association in fun and fun[association]:
                    self.page.append(" dans le/la " + self.__hyperlink(fun[association]))

                if administration in fun and fun[administration]:
                    print("administration", fun[administration], "in", self.url,"++++++++++++++++++++++")

                if sociability_body in fun and fun[sociability_body]:
                    print("sociability_body", fun[sociability_body],"in", self.url,"+++++++++++++++++++++++++")

                if political_body in fun and fun[political_body]:
                    groups = self.__parethisisOff(fun[political_body])
                    if groups[0] is not None:
                        arg = '' if groups[1] is None else ' ' + groups[1]
                        self.page.append(" de " + self.__hyperlink(groups[0]) + arg)
                """
                    self.page.append(" de " + self.__hyperlink(fun[company]))
                    arg = self.__parethisisOff(fun[political_body])
                    if arg[1]:
                        self.page.append(" dans le/la " + arg[1].strip(' ()'))
                """
                # what about organe politique
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
        payload = "".join([x[1] for x in self.pages if x[0] != date(1, 1, 1)])
        print(payload)
