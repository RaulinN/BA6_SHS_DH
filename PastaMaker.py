import string
import keywords as keys

class PastaMaker:

    def __init__(self):
        """Create a page"""
        self.page = []

    def __endLine(self):
        self.page.append('\n')

    def __hyperlink(self, word):
        return '[[' + str(word) + ']]'

    def __spaceTime(self, time, space):
        time = '-' if time is None else self.__hyperlink(time)
        space = '-' if space is None else self.__hyperlink(space)
        self.page.append(' ' + time + '/' + space + ' ')

    def __default(self, value, default = '-'):
        return default if value is None else value

    def __sources(self, sources):
        # to see
        for i in sources:
            self.page.append('[' + str(i) + ']')
            self.__endLine()

    def addIngredient(self, ingredient):
        """Add an event to the page"""

        if keys.birth in ingredient:
            spice = ingredient[keys.birth]
            self.__spaceTime(spice[keys.date], spice[keys.location])
            self.page.append(self.__hyperlink("Naissance") + " de " + spice[keys.star])
            self.__endLine()

        if keys.death in ingredient:
            spice = ingredient[keys.birth]
            self.__spaceTime(spice[keys.date], spice[keys.location])
            self.page.append(self.__hyperlink("Décès") + " de " + spice[keys.star])
            self.__endLine()

    def cook(self):
        """ Make the past -- I mean returns the page created as a long string"""
        # TODO call the wikipast magic class
        return string.join(self.page, '')
