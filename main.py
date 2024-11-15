import feeds
import api
from time import sleep
from jinja2 import Template
from datetime import datetime
from dateutil import parser
from os import makedirs
import os.path
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="update.log", level=logging.INFO)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


if not os.path.isdir('cache'):
    makedirs('cache')
if not os.path.isdir('site'):
    makedirs('cache')
if not os.path.isdir('site/feed'):
    makedirs('site/feed')


setters = api.get_setters()
if not setters:
    logger.error("Could not get setter list")
    exit()


def has_recent(username, last_published):
    if not os.path.exists(f"cache/{username}.json"):
        return True
    feed_time = datetime.fromtimestamp(
        os.path.getmtime(f"cache/{username}.json")
    )
    pub_time = parser.parse(last_published[:16])
    return pub_time > feed_time


new_crosswords = False
no_errors = True
for setter in setters:
    user = setter.get("username", "")
    last_published = setter.get("last_published", "")
    if not user:
        logger.error("Setter without username")
        no_errors = False
        continue
    if not last_published:
        logger.error("Setter without last published puzzle")
        no_errors = False
        continue

    if has_recent(user, last_published):
        crosswords = api.get_setter_crosswords(user)
        sleep(1)
        if not crosswords:
            no_errors = False
            continue
        with open(f"cache/{user}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(crosswords))
        new_crosswords = True

    else:
        # Use cached setter data if cached data is more recent than
        # the last puzzle they published
        with open(f"cache/{user}.json", "r", encoding="utf-8") as f:
            crosswords = json.loads(f.read())

    feed = feeds.generate_setter_feed(user, crosswords)
    if not feed:
        no_errors = False
        continue

    with open(f"site/feed/{user}.rss", "w", encoding="utf-8") as f:
        f.write(feed)


if new_crosswords:
    all_crosswords = api.get_all_recent_crosswords()
    feed = feeds.generate_global_feed(all_crosswords)
    if not feed:
        no_errors = False
    with open("site/feed/ALL_SETTERS.rss", "w", encoding="utf-8") as f:
        f.write(feed)
    if no_errors:
        logger.info("Updated feeds with no errors")


with open("template.html", "r", encoding="utf-8") as f:
    template = Template(f.read())
    output = template.render(setters=setters)

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(output)
