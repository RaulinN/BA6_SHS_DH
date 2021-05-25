import requests

from model.network import Query, Queries
from model.objects.JsonObject import JsonObject
import BotIdentification  # File not pushed on github
import typing


class QueryManager:
    """
    Singleton class that manages network queries/answer

    Attributes:
      - __instance: QueryManager | None
            Singleton instance of the QueryManager (or None if no instance exists yet)
      - session: Session
            Active connection between bot and wikipast's server
      - loginToken: str
            Secret and unique authentication token required for data modification
      - csrfToken: str
            Secret and unique token used to prevent CSRF attacks (Synchronizer
            token pattern technique)
    """

    class __QueryManager:
        """Inner class used to implement the singleton design pattern"""

        def __init__(self):
            self.session = requests.Session()

    __instance = None  # Singleton QueryManager object

    def __init__(self):
        if not QueryManager.__instance:
            QueryManager.__instance = QueryManager.__QueryManager()
            self.loginToken, self.csrfToken = self.__getCredentials()

    def __getattr__(self, item):
        return getattr(self.__instance, item)

    def __getCredentials(self):
        """Returns EliteBot's credentials: loginToken & csrfToken"""

        # GET request to fetch login token
        query: Query = Queries.fetchLoginTokenQuery()
        queryAnswer = self.sendGetQuery(query)
        loginToken = queryAnswer.json['query']['tokens']['logintoken']

        # POST request to log in
        query: Query = Queries.postLoginQueryQuery(BotIdentification.ID_USERNAME, BotIdentification.ID_PASSWORD,
                                                   loginToken)
        self.sendPostQuery(query)

        # GET request to fetch CSRF token
        query: Query = Queries.fetchCsrfTokenQuery()
        queryAnswer = self.sendGetQuery(query)
        csrfToken = queryAnswer.json['query']['tokens']['csrftoken']

        return loginToken, csrfToken

    @staticmethod
    def handleQueryAnswer(jsonAnswer: JsonObject) -> None:
        if 'error' in jsonAnswer.json.keys() or 'warning' in jsonAnswer.json.keys():
            jsonAnswer.prettyPrint()

    def sendGetQuery(self, query: Query) -> JsonObject:
        answer: JsonObject = JsonObject(self.session.get(url=query.url, params=query.params).json())
        self.handleQueryAnswer(answer)
        return answer

    def sendPostQuery(self, query: Query) -> JsonObject:
        answer: JsonObject = JsonObject(self.session.post(url=query.url, data=query.params).json())
        self.handleQueryAnswer(answer)
        return answer

    def __editPage(self, queryGenerationFunction, pageTitle: str, payload: str, createOnly: bool):
        # POST request to edit a page
        query: Query = queryGenerationFunction(
            self.csrfToken,
            pageTitle,
            payload,
            createOnly=createOnly
        )
        self.sendPostQuery(query)

    def prependContentPage(self, pageTitle: str, payload: str, createOnly: bool = True):
        return self.__editPage(Queries.postPrependPageQuery, pageTitle, payload, createOnly)

    def setContentPage(self, pageTitle: str, payload: str, createOnly: bool = True):
        return self.__editPage(Queries.postSetPageQuery, pageTitle, payload, createOnly)

    def appendContentPage(self, pageTitle: str, payload: str, createOnly: bool = True):
        return self.__editPage(Queries.postAppendPageQuery, pageTitle, payload, createOnly)

    def fetchPages(self, pageTitle: str):
        query: Query = Queries.fetchPageContent(pageTitle)
        answer = self.sendGetQuery(query)

        pages = answer.json["query"]["pages"]
        return pages

    def fetchPageContent(self, pageTitle: str) -> typing.Optional[str]:
        pages = self.fetchPages(pageTitle)
        keys = list(pages.keys())

        if len(keys) == 0 or '-1' in keys:
            return None
        else:
            return pages[keys[0]]["revisions"][0]["slots"]["main"]["*"]

    @staticmethod
    def __pageContentDiff(localPageContent: str, remotePageContent: str) -> str:
        contentList: list = remotePageContent.splitlines()
        newEntries: str = ""

        for entry in localPageContent.splitlines():
            if entry not in contentList:
                newEntries += entry

        return newEntries

    @staticmethod
    def __shortenPageLinks(payload: str, pageTitle: str, fullTitle: str) -> str:
        return payload.replace("[[{}]]".format(fullTitle), "[[{} | {}]]".format(fullTitle, pageTitle))

    def uploadInformation(self, pageTitle: str, eliteId: str, payload: str):
        """
        Update a page describing elite <pageTitle> depending on remote information

        :param pageTitle: the page title (without id) corresponding to the elite name
        :param eliteId: the id of the elite (number in the url of the elite on db)
        :param payload: the payload that should be uploaded on the corresponding page
        """

        fullTitle = "{} ({})".format(pageTitle, eliteId)

        # Ask for the page (if any) with title <fullTitle>
        content = self.fetchPageContent(fullTitle)

        if content is None:
            # There's no page with correct title (and id)

            content = self.fetchPageContent(pageTitle)
            if content is None:
                # There's no page with correct simple title (no id)

                # Create a new page with <fullTitle> and set its content to the payload
                self.setContentPage(fullTitle, self.__shortenPageLinks(payload, pageTitle, fullTitle))
            else:
                # There's a page with correct simple title (no id), probably user created
                if "??????????????????????" in content:  # TODO modify elite url
                    # EliteBot is virtually sure the page is about the correct elite
                    newEntries: str = self.__pageContentDiff(payload, content)

                    if newEntries != "":
                        # The page is NOT up-to-date
                        self.appendContentPage(pageTitle, newEntries, createOnly = False)
                else:
                    # EliteBot cannot certify that the page is about the correct elite
                    self.setContentPage(fullTitle, self.__shortenPageLinks(payload, pageTitle, fullTitle))
        else:
            # A page with correct title (and id) already exists, very likely created by EliteBot
            newEntries: str = self.__pageContentDiff(payload, content)

            if newEntries != "":
                # The page is NOT up-to-date
                self.appendContentPage(fullTitle, self.__shortenPageLinks(newEntries, pageTitle, fullTitle), createOnly = False)


def main():
    uploadManager: QueryManager = QueryManager()
    # See the result here:
    # http://wikipast.epfl.ch/wiki/EliteBot:_test
    # uploadManager.appendContentPage("EliteBot: test", "Hello world!", createOnly = False)
    content = """
*  [[1971]] / -. [[Naissance]] de [[Regina Elisabeth  Aebi-Müller (84684) | Regina Elisabeth  Aebi-Müller]] [source]
*  [[2000]] / [[Suisse]]. [[Diplôme]]: [[Regina Elisabeth  Aebi-Müller (84684) | Regina Elisabeth  Aebi-Müller]] diplomée de [[UniBe]] : Doctorat en droit [source]
*  [[2005]] / -. [[Regina Elisabeth  Aebi-Müller (84684) | Regina Elisabeth  Aebi-Müller]] est professeur ordinaire à [[UniLu]] (faculté de droit) [source]
*  [[2010]] / -. [[Regina Elisabeth  Aebi-Müller (84684) | Regina Elisabeth  Aebi-Müller]] est doyen à [[UniLu]] (Rechtswissenschaftliche Fakultät) [source]
*  [[2015]] / -. [[Regina Elisabeth  Aebi-Müller (84684) | Regina Elisabeth  Aebi-Müller]] est Membre à [[Fonds national suisse de la recherche scientifique]] (conseil national de la recherche ) [source]
    """
    uploadManager.setContentPage("Regina Elisabeth Aebi-Müller (84684)", content, createOnly = False)

    # uploadManager.fetchPageContent("Hugo Allemann")


if __name__ == '__main__':
    main()
