import requests

from model.network import Query, Queries
from model.objects.JsonObject import JsonObject
import BotIdentification  # File not pushed on github

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
        query = Queries.fetchLoginTokenQuery()
        queryAnswer = self.sendGetQuery(query)
        loginToken = queryAnswer.json['query']['tokens']['logintoken']

        # POST request to log in
        query = Queries.postLoginQueryQuery(BotIdentification.ID_USERNAME, BotIdentification.ID_PASSWORD, loginToken)
        self.sendPostQuery(query)

        # GET request to fetch CSRF token
        query = Queries.fetchCsrfTokenQuery()
        queryAnswer = self.sendGetQuery(query)
        csrfToken = queryAnswer.json['query']['tokens']['csrftoken']

        return loginToken, csrfToken


    @staticmethod
    def handleQueryAnswer(jsonAnswer: JsonObject) -> None:
        if 'error' in jsonAnswer.json.keys():
            jsonAnswer.prettyPrint()


    def sendGetQuery(self, query: Query) -> JsonObject:
        answer = JsonObject(self.session.get(url = query.url, params = query.params).json())
        self.handleQueryAnswer(answer)
        return answer


    def sendPostQuery(self, query: Query) -> JsonObject:
        answer = JsonObject(self.session.post(url = query.url, data = query.params).json())
        self.handleQueryAnswer(answer)
        return answer


    def testSendAppendMessage(self):
        # See the result here:
        # http://wikipast.epfl.ch/wiki/EliteBot:_test

        # POST request to edit a page
        query = Queries.postAppendPageQuery(
            self.csrfToken,
            "EliteBot: test",
            "Hello world!",
            createOnly = False
        )
        self.sendPostQuery(query)



def main():
    uploadManager = QueryManager()
    uploadManager.testSendAppendMessage()


if __name__ == '__main__':
    main()

