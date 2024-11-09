from requests import request
import logging

logger = logging.getLogger(__name__)

API_URL = "https://mycrossword.co.uk/api/crossword"
SETTER_REQUEST = "/getpublished?type=all&sort=n&timeWindow=m&setter={username}&limit={limit}"
ALL_RECENT_REQUEST = "/getpublished?userId=894&type=all&sort=n&timeWindow=m&limit={limit}"


def get_setters():
    setters_response = request(
        "GET",
        API_URL + "/getsetters"
    )
    if setters_response.status_code != 200:
        logger.error("Failed to get setters")
        return False
    setters = setters_response.json()
    return setters


def get_setter_crosswords(username):
    crosswords_response = request(
        "GET",
        API_URL + SETTER_REQUEST.format(username=username, limit=10)
    )
    if crosswords_response.status_code != 200:
        logger.error(
            f"Failed to get crosswords for setter {username},"
            f"status {crosswords_response.status_code}")
        return False
    crosswords = crosswords_response.json()["crosswords"]
    return crosswords

def get_all_recent_crosswords():
    response = request(
        "GET",
        API_URL + ALL_RECENT_REQUEST.format(limit=20)
    )
    if response.status_code != 200:
        logger.error(
            f"Failed to get global crossword data, status {response.status_code}")
        return False
    crosswords = response.json()["crosswords"]
    return crosswords
