from feedgen.feed import FeedGenerator
from datetime import datetime
from time import time
import logging

SITE_DOMAIN = "https://mycrsswrd.co.uk"

logger = logging.getLogger(__name__)


def convert_date(date):
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
        entry.published(convert_date(cw_date))
    entry.description(
        f"<img src='{image}'>"
        f"<br>Photo by <a href='{photographer_link}'>{photographer}</a>"
    )
    entry.link(
        {"href": f"https://mycrossword.co.uk/{cw_type}/{crossword['published_num']}"}
    )
    entry.dc.dc_creator(f"{username}")
    entry.guid(
        f"https://mycrossword.co.uk/{cw_type}/{cw_num}",
        permalink=True
    )


def generate_global_feed(crosswords):
    feed = FeedGenerator()
    feed.load_extension("dc")
    feed.title(
        "MyCrossword"
    )
    feed.link({"href": "https://mycrossword.co.uk/"})
    feed.link(
        {"href": SITE_DOMAIN + "/feed/ALL_SETTERS.rss", "rel": "self"})
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
    setter.link(
        {"href": SITE_DOMAIN + f"/feed/{username}.rss", "rel": "self"})
    setter.description(f"Latest MyCrossword puzzles from {username}")
    for crossword in crosswords:
        make_entry(setter, username, crossword)
    return setter.rss_str(pretty=True).decode("utf-8")
