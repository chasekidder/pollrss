'''
Copyright 2020 Chase Kidder

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import datetime
from . import rfeed
from .models import Feed, FeedField, Item, ItemField

# Add new db entry
#from .models import Feed
#f = Feed(elements={}, posts={})
#f.save()



class FeedObj():
    elements = {}
    items = {}


class ItemObj():
    elements = {}


def create_rss_feed(feed_id: int) -> rfeed.Feed:
    optional_elems = {
                "language": None,
                "copyright": None,
                "managingEditor": None,
                "webMaster": None,
                "pubDate": None,
                "lastBuildDate": None,
                "categories": None,
                "generator": None,
                "docs": None,
                "cloud": None,
                "ttl": None,
                "image": None,
                "rating": None,
                "textInput": None,
                "skipHours": None,
                "skipDays": None,
                "items": None,
                "extensions": None
            }

    feed_obj = __create_feed(feed_id)

    feed_obj.items = __create_rss_items(feed_obj.items)

    rss_feed = rfeed.Feed(
            title=feed_obj.elements["title"],
            link=feed_obj.elements["link"],
            description=feed_obj.elements["description"]
        )

    for element in feed_obj.elements:
        try:
            optional_elems[element] = feed_obj.elements[element]

        except:
            pass
    
    rss_feed.language = optional_elems["language"]
    rss_feed.copyright = optional_elems["copyright"]
    rss_feed.managingEditor = optional_elems["managingEditor"]
    rss_feed.webMaster = optional_elems["webMaster"]
    rss_feed.pubDate = optional_elems["pubDate"]
    rss_feed.lastBuildDate = optional_elems["lastBuildDate"]
    rss_feed.categories = optional_elems["categories"]
    rss_feed.generator = optional_elems["generator"]
    rss_feed.docs = optional_elems["docs"]
    rss_feed.cloud = optional_elems["cloud"]
    rss_feed.ttl = optional_elems["ttl"]
    rss_feed.image = optional_elems["image"]
    rss_feed.rating = optional_elems["rating"]
    rss_feed.textInput = optional_elems["textInput"]
    rss_feed.skipHours = optional_elems["skipHours"]
    rss_feed.skipDays = optional_elems["skipDays"]
    rss_feed.items = optional_elems["items"]
    rss_feed.extensions = optional_elems["extensions"]

    return rss_feed


def __create_rss_items(items: dict) -> list:
    rss_items = []

    optional_elems = {
                    "title": None,
                    "link": None,
                    "description": None,
                    "author": None,
                    "creator": None,
                    "categories": None,
                    "comments": None,
                    "enclosure": None,
                    "guid": None,
                    "pubDate": None,
                    "source": None,
                    "extensions": None
                }

    for item in items:
        rss_item = rfeed.Item(title=item)

        for element in items[item].elements:
            try:
                optional_elems[element] = items[item].elements[element]

            except:
                pass

        rss_item.title = optional_elems["title"]
        rss_item.link = optional_elems["link"]
        rss_item.description = optional_elems["description"]
        rss_item.author = optional_elems["author"]
        rss_item.creator = optional_elems["creator"]
        rss_item.categories = optional_elems["categories"]
        rss_item.comments = optional_elems["comments"]
        rss_item.enclosure = optional_elems["enclosure"]
        rss_item.guid = optional_elems["guid"]
        rss_item.pubDate = optional_elems["pubDate"]
        rss_item.source = optional_elems["source"]
        rss_item.extensions = optional_elems["extensions"]

        rss_items.append(rss_item)

    breakpoint()
    return rss_items


def __create_feed(feed_id: int) -> FeedObj:
    xml_feed = FeedObj()
    db_feed = Feed.objects.get(pk=feed_id)

    for field in db_feed.feedfield_set.all():
        xml_feed.elements[field.name] = field.value

    xml_feed.items = __create_items(xml_feed)

    return xml_feed


def __create_items(db_feed: Feed) -> dict:
    xml_items = {} 
    for item in db_feed.items:
        xml_items[item.fingerprint] = ItemObj()

        for field in item.itemfield_set.all():
            xml_items[item.fingerprint].elements[field.name] = field.value

    return xml_items

    



