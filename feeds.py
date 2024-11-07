from requests import request
from feedgen.feed import FeedGenerator
from datetime import datetime
from time import time
import logging

logger = logging.getLogger(__name__)


def get_setters():
    setters_response = request(
        "GET",
        "https://mycrossword.co.uk/api/crossword/getsetters"
    )
    if setters_response.status_code != 200:
        logger.error("Failed to get setters")
        return False
    setters = setters_response.json()
    return setters


def get_setter_crosswords(username):
    crosswords_response = request(
        "GET",
        f"https://mycrossword.co.uk/api/crossword/getpublished?type=all&sort=n&timeWindow=m&setter={username}&limit=10"
    )
    if crosswords_response.status_code != 200:
        logger.error(
            f"Failed to get crosswords for setter {username},"
            f"status {crosswords_response.status_code}")
        return False
    crosswords = crosswords_response.json()["crosswords"]
    return crosswords


def get_setter_info(username):
    info_response = request(
        "GET",
        f"https://mycrossword.co.uk/api/profile/get?username={username}"
    )
    if info_response.status_code != 200:
        logger.error(
            f"Failed to get profile for setter {username}, status {info_response.status_code}")
        return False
    info = info_response.json()
    return info


def parse_date(date):
    dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")


def make_entry(feed, username, crossword):
    cw_type = crossword.get("type", "unknown")
    cw_num = crossword.get("published_num", "unknown")
    cw_date = crossword.get("published", "")
    image = crossword.get("image_url_small", "")
    photographer = crossword.get("image_photographer", "")
    photographer_link = crossword.get("image_photographer_link", "")
    entry = feed.add_entry()
    entry.title(
        f"{cw_type.title()} crossword No {cw_num} by {username}")
    entry.author(
        {"name": username, "uri": f"https://mycrossword.co.uk/{username}"}
    )
    if cw_date:
        entry.published(parse_date(cw_date))
    entry.description(
        f"<p>Set by <a href='https://mycrossword.co.uk/{username}'>{username}</a></p>"
        f"<img src='{image}'>"
        f"<br>Photo by <a href='{photographer_link}'>{photographer}</a>"
    )
    entry.link(
        {"href": f"https://mycrossword.co.uk/{type}/{crossword['published_num']}"}
    )
    entry.guid(
        f"https://mycrossword.co.uk/{cw_type}/{cw_num}",
        permalink=True
    )


def generate_global_feed():
    response = request(
        "GET",
        "https://mycrossword.co.uk/api/crossword/"
        "getpublished?userId=894&type=all&sort=n&timeWindow=m&limit=20"
    )
    if response.status_code != 200:
        logger.error(
            f"Failed to get global crossword data, status {response.status_code}")
        return False
    crosswords = response.json()["crosswords"]
    feed = FeedGenerator()
    feed.title(
        "MyCrossword"
    )
    feed.link({"href": "https://mycrossword.co.uk/"})
    feed.link(
        {"href": "https://mycrsswrd.co.uk/feed/ALL_SETTERS.xml", "rel": "self"})
    feed.description("Latest MyCrossword puzzles")
    for crossword in crosswords:
        make_entry(feed, crossword["username"], crossword)
    return feed.rss_str(pretty=True).decode("utf-8")


def generate_setter_feed(username, crosswords):
    setter = FeedGenerator()
    setter.title(
        f"{username} · MyCrossword"
    )
    setter.link({"href": f"https://mycrossword.co.uk/{username}"})
    setter.author(
        {"name": username, "uri": f"https://mycrossword.co.uk/{username}"}
    )
    setter.link({"href": f"https://mycrsswrd.co.uk/{username}", "rel": "self"})
    setter.description(f"Latest MyCrossword puzzles from {username}")
    for crossword in crosswords:
        make_entry(setter, username, crossword)
    return setter.rss_str(pretty=True).decode("utf-8")


def process_setter(username):
    feed = generate_setter_feed(username, info, crosswords)
    return feed
