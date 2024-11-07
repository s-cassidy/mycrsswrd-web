import feeds
from time import sleep
from jinja2 import Template
from datetime import datetime
from dateutil import parser
import os.path
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="update.log",
                    encoding="utf-8", level=logging.INFO)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

setters = feeds.get_setters()

if not setters:
    logger.error("Could not get setter list")
    exit()


def check_recent(username, last_published):
    if not os.path.exists(f"cache/{username}.json"):
        return True
    feed_time = datetime.fromtimestamp(
        os.path.getmtime(f"cache/{username}.json")
    )
    pub_time = parser.parse(last_published[:16])
    return pub_time > feed_time


updated = False
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

    if check_recent(user, last_published):
        crosswords = feeds.get_setter_crosswords(user)
        sleep(3)
        if not crosswords:
            no_errors = False
            continue
        with open(f"cache/{user}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(crosswords))
        updated = True
    else:
        with open(f"cache/{user}.json", "r", encoding="utf-8") as f:
            crosswords = json.loads(f.read())
    feed = feeds.generate_setter_feed(user, crosswords)
    if not feed:
        no_errors = False
        continue
    with open(f"site/feed/{user}.xml", "w", encoding="utf-8") as f:
        f.write(feed)

if updated:
    feed = feeds.generate_global_feed()
    if not feed:
        no_errors = False
    with open("site/feed/ALL_SETTERS.xml", "w", encoding="utf-8") as f:
        f.write(feed)
    if no_errors:
        logger.info("Updated feeds with no errors")


with open("template.html", "r", encoding="utf-8") as f:
    template = Template(f.read())
    output = template.render(setters=setters)

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(output)
