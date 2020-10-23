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


class FeedObj():
    """Database Feed Object

    Args:
        None

    Elements:
        elements (Dict): Dictionary of feed element names and values.
        items (Dict): Dictionary of item objects (ItemObj).
    """
    elements = {}
    items = {}


class ItemObj():
    """Database Feed Item Object

    Args:
        None

    Elements:
        elements (Dict): Dictionary of item element names and values.
    """
    elements = {}


def create_rss_feed(feed_id: int) -> rfeed.Feed:
    """Create a finalized rfeed RSS feed from information in database.

    Args:
        feed_id (int): Unique database feed identifier.

    Returns:
        rfeed.Feed: Finalized rfeed Feed object.
    """
    optional_elems = {
                "language": None,
                "copyright": None,
                "managingEditor": None,
                "webMaster": None,
                "pubDate": None,
                "lastBuildDate": None,
                "categories": [],
                "generator": None,
                "docs": None,
                "cloud": None,
                "ttl": None,
                "image": None,
                "rating": None,
                "textInput": None,
                "skipHours": None,
                "skipDays": None,
                "extensions": []
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

    if feed_obj.items == False:
        rss_feed.items = []
    else:
        rss_feed.items = feed_obj.items
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
    rss_feed.extensions = optional_elems["extensions"]

    return rss_feed


def __create_rss_items(items: dict) -> list:
    """Convert a list of database feed items into a list of rfeed item objects.

    Args:
        items (dict): Dictionary of database items identified by fingerprint.

    Returns:
        list: List of finalized rfeed item objects.
    """
    rss_items = []

    optional_elems = {
                    "title": None,
                    "link": None,
                    "description": None,
                    "author": None,
                    "creator": None,
                    "categories": [],
                    "comments": None,
                    "enclosure": None,
                    "guid": None,
                    "pubDate": None,
                    "source": None,
                    "extensions": []
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

    return rss_items


def __create_feed(feed_id: int) -> FeedObj:
    """Creates feed object to contain database feed fields and items for a specific feed.

    Args:
        feed_id (int): Unique feed identifier from database.

    Returns:
        FeedObj: Object containing all feed info and items.
    """
    xml_feed = FeedObj()
    db_feed = Feed.objects.get(pk=feed_id)
    items = [""]

    for field in db_feed.feedfield_set.all():
        xml_feed.elements[field.name] = field.value

    xml_feed.items = __create_items(db_feed)

    return xml_feed


def __create_items(db_feed: Feed) -> dict:
    """Create a dictionary of items from all related items in database. Identified by fingerprint.

    Args:
        db_feed (Feed): The database feed object.

    Returns:
        dict: Related database items tagged by fingerprint.
    """

    xml_items = {} 
    for item in db_feed.item_set.all():
        xml_items[item.fingerprint] = ItemObj()

        for field in item.itemfield_set.all():
            xml_items[item.fingerprint].elements[field.name] = field.value

    return xml_items

    



