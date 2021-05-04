from enum import Enum

from model.network.Query import Query


ANSWER_FORMAT = 'json'  # (query and) answer format


def fetchLoginTokenQuery() -> Query:
    """Generates a (GET) request payload to fetch login token"""
    return Query({
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": ANSWER_FORMAT
    })

def postLoginQueryQuery(username: str, password: str, loginToken: str) -> Query:
    """
    Generates a (POST) request payload to log in

    Attributes:
      - username: str => EliteBot's wikipast username
      - password: str => EliteBot's wikipast password
      - loginToken: str => EliteBot's previously generated login token
    """

    return Query({
        "action": "login",
        "lgname": username,
        "lgpassword": password,
        "lgtoken": loginToken,
        "format": ANSWER_FORMAT
    })


def fetchCsrfTokenQuery() -> Query:
    """Generates a (GET) request payload to fetch CSRF token"""
    return Query({
        "action": "query",
        "meta": "tokens",
        "format": ANSWER_FORMAT
    })


class EditMethodType(Enum):
    """Enumeration of all possible way to modify a page"""
    PREPEND = 'prependtext'
    SET = 'text'
    APPEND = 'appendtext'


def __postEditPageQuery(csrfToken: str, editMethod: EditMethodType, pageTitle: str, payload: str, createOnly: bool) -> Query:
    """
    Generates a (POST) request payload to edit a page

    Attributes:
      - csrfToken: str
            EliteBot's previously generated csrf token
      - editMethod: EditMethodType
            Either prepend, set, or append text to the page
      - pageTitle: str
            Title of the page that should be modified
      - payload: str
            Text payload to be sent
      - createOnly: boolean
            If createOnly is set to true, then the page is modified iff it doesn't yet
            exist. If createOnly is set to false, then the page will be modified regardless
    """

    params = {
        "action": "edit",
        "title": pageTitle,
        "token": csrfToken,
        "format": ANSWER_FORMAT,
        editMethod.value: payload,
        "bot": "true",
    }

    if createOnly:
        params["createonly"] = "true"

    return Query(params)


def postPrependPageQuery(csrfToken: str, pageTitle: str, payload: str, createOnly: bool = True) -> Query:
    """Generates a (POST) request payload to prepend a payload to a page"""
    return __postEditPageQuery(csrfToken, EditMethodType.PREPEND, pageTitle, payload, createOnly)

def postSetPageQuery(csrfToken: str, pageTitle: str, payload: str, createOnly: bool = True) -> Query:
    """Generates a (POST) request payload to set a payload on a page"""
    return __postEditPageQuery(csrfToken, EditMethodType.SET, pageTitle, payload, createOnly)

def postAppendPageQuery(csrfToken: str, pageTitle: str, payload: str, createOnly: bool = True) -> Query:
    """Generates a (POST) request payload to append a payload to a page"""
    return __postEditPageQuery(csrfToken, EditMethodType.APPEND, pageTitle, payload, createOnly)
