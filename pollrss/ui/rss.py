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
from email.utils import parsedate_to_datetime

from . import rfeed
from .models import Feed, FeedField, Item, ItemField
from django.db import transaction

import requests
from bs4 import BeautifulSoup

import hashlib


class FeedObj():
    """Database Feed Object

    Args:
        None

    Elements:
        elements (Dict): Dictionary of feed element names and values.
        items (Dict): Dictionary of item dictionaries.
    """
    elements = {}
    items = {}


def create_rss_feed_from_object(feed_id: int) -> rfeed.Feed:
    """Create an RSS Feed from FeedObj.

    Args:
        feed_id (int): Unique database feed identifier.

    Returns:
        rfeed.Feed: Finalized rfeed Feed object.
    """
    elements = {
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

    feed_obj = read_feed_from_database(feed_id)

    rss_feed = rfeed.Feed(
            title=feed_obj.elements["title"],
            link=feed_obj.elements["link"],
            description=feed_obj.elements["description"]
        )

    rss_feed.language = elements["language"]
    rss_feed.copyright = elements["copyright"]
    rss_feed.managingEditor = elements["managingEditor"]
    rss_feed.webMaster = elements["webMaster"]
    rss_feed.pubDate = elements["pubDate"]
    rss_feed.lastBuildDate = elements["lastBuildDate"]
    rss_feed.categories = elements["categories"]
    rss_feed.generator = elements["generator"]
    rss_feed.docs = elements["docs"]
    rss_feed.cloud = elements["cloud"]
    rss_feed.ttl = elements["ttl"]
    rss_feed.image = elements["image"]
    rss_feed.rating = elements["rating"]
    rss_feed.textInput = elements["textInput"]
    rss_feed.skipHours = elements["skipHours"]
    rss_feed.skipDays = elements["skipDays"]
    rss_feed.extensions = elements["extensions"]

    for item in feed_obj.items:
        rss_feed.items.append(__convert_to_rss_item(feed_obj.items[item]))

    return rss_feed


def __process_element(value: str, name: str):
    """Process RSS element into appropriate format for rfeed.

    Args:
        calue (str): Element value.

    Returns:
        (Optional) str: Non specific processed value.
        (Optional) datetime: Date time object from RFC 822 formatted date value.
        (Optional) rfeed.Guid: Guid object.
    """

    #NOTE: Currently anything here that is passed is stripped from the feed.
    if name == "pubDate":
        return parsedate_to_datetime(value)
    elif name == "lastBuildDate":
        return parsedate_to_datetime(value)
    elif name == "guid":
        #TODO: Check for isPermaLink
        return rfeed.Guid(value, False) 
    elif name == "source":
        #TODO: Process element
        pass
    elif name == "categories":
        #TODO: Process element
        pass
    elif name == "extensions":
        #TODO: Process element
        pass
    elif name == "cloud":
        #TODO: Process element
        pass
    elif name == "image":
        #TODO: Process element
        pass
    elif name == "textImage":
        #TODO: Process element
        pass
    elif name == "skipHours":
        #TODO: Process element
        pass
    elif name == "skipDays":
        #TODO: Process element
        pass
    elif name == "enclosure":
        #TODO: Process element
        pass
    else:
        return value


def __convert_to_rss_item(item: dict) -> rfeed.Item:
    """Convert feed item element dictionary into an rfeed item object.

    Args:
        item (dict): Dictionary of item elements.

    Returns:
        rfeed.Item: Finalized rfeed item object.
    """
    elements = {
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

    rss_item = rfeed.Item(title=item["title"])
    
    for element in elements:
        try:
            elements[element] = item[element]
        except:
            pass

    rss_item.title = elements["title"]
    rss_item.link = elements["link"]
    rss_item.description = elements["description"]
    rss_item.author = elements["author"]
    rss_item.creator = elements["creator"]
    rss_item.categories = elements["categories"]
    rss_item.comments = elements["comments"]
    rss_item.enclosure = elements["enclosure"]
    rss_item.guid = elements["guid"]
    rss_item.pubDate = elements["pubDate"]
    rss_item.source = elements["source"]
    rss_item.extensions = elements["extensions"]

    return rss_item


def read_feed_from_database(feed_id: int) -> FeedObj:
    """Create FeedObj from Feed entry in database.

    Args:
        feed_id (int): Unique database feed identifier.

    Returns:
        FeedObj: Database feed object containing all items and elements.
    """
    rss_feed = FeedObj()
    db_feed = Feed.objects.get(pk=feed_id)

    # Read feed elements
    for feed_field in db_feed.feedfield_set.all():
        rss_feed.elements[feed_field.name] = __process_element(feed_field.value, feed_field.name)

    # Read all feed items
    for item in db_feed.item_set.all():
        rss_feed.items[item.fingerprint] = {}

        # Read all item elements
        for item_field in item.itemfield_set.all():
            rss_feed.items[item.fingerprint][item_field.name] = __process_element(item_field.value, item_field.name)

    return rss_feed
    

#TODO: Need function that updates existing feeds in the database. Eg. check new feed against database fingerprints and only add new ones.


def write_feed_to_database(feed: FeedObj, rss_link: str) -> int:
    """Write a feed object to the database and return the Feed ID.

    Args:
        feed (FeedObj): Feed object to be written.
        rss_link (str): Source RSS feed link.

    Returns:
        int: New database Feed ID. (0 = Not Created)
    """

    # Check for feed existence
    if (__feed_exists(rss_link)):
        print("Feed Already Exists!")

    else:
        #TODO: If there is an Integrity Error Here, that means that a fingerprint is a duplicate. We need to check for duplicates!!!!

        # Start a bulk database transaction
        with transaction.atomic():

            # Create a new feed entry in database
            db_feed = Feed()
            db_feed.rss_link = rss_link
            db_feed.save()

            # Add all feed elements to database
            for feed_field_name in feed.elements:
                feed_field = FeedField(feed=db_feed)
                feed_field.name = feed_field_name
                feed_field.value = feed.elements[feed_field_name]
                feed_field.required = True
                feed_field.save()

            # Create new item entries in database
            for item_name in feed.items:
                item = Item(feed=db_feed)
                item.fingerprint = item_name
                item.save()

                # Add all item elements to database
                for item_field_name in feed.items[item_name]:
                    item_field = ItemField(item=item)
                    item_field.name = item_field_name
                    item_field.value = feed.items[item_name][item_field_name]
                    item_field.save()

        return db_feed.pk
    
    return 0


def __feed_exists(link: str) -> bool:
    """Check if feed exists in database.

    Args:
        link (str): Feed source link.

    Returns:
        bool: Feed existance in database status.
    """
    try:
        feeds = Feed.objects.get(rss_link__exact=link)
    except Feed.DoesNotExist:
        return False

    return True

    
# TODO: Refactor read feed from link functions. Change fingerprint to GUID hash?

def read_feed_from_link(link: str) -> FeedObj:
    """Create a FeedObj from a link.

    Args:
        link (str): RSS feed source link.

    Returns:
        FeedObj: Feed object containing all items and elements.
    """
    try:
        response = requests.get(link)

    except Exception as e:
        print("RSS Feed fetch FAILED!" + e)
        return 1

    soup = BeautifulSoup(response.content, features='xml')

    rss_feed = soup.find("rss")
    
    if rss_feed == False:
        print("RSS Feed not found!")
        return 1
    
    else:
        print("Feed Found")

    feed = FeedObj()

    feed.elements = __parse_feed_elements_xml(rss_feed)
    feed.items = __parse_feed_items_xml(rss_feed)

    return feed
     
        
def __parse_feed_elements_xml(xml):
    
    elements = {}
    optional_elems = [
                    "title",
                    "link",
                    "description",
                    "author",
                    "creator",
                    "categories",
                    "comments",
                    "enclosure",
                    "guid",
                    "pubDate",
                    "source",
                    "extensions"
                    ]

    for element in optional_elems:
        r = xml.find(element)

        if r == None:
            pass

        else:
            try:
                elements[element] = r.contents[0]
            except:
                pass
    
    return elements


def __parse_feed_items_xml(xml):
    final_items = {}
    elements = {}
    optional_elems = [
                    "title",
                    "link",
                    "description",
                    "author",
                    "creator",
                    "categories",
                    "comments",
                    "enclosure",
                    "guid",
                    "pubDate",
                    "source",
                    "extensions"
                ]
    fingerprint = ""

    items = xml.findAll("item")

    for item in items:
        for element in optional_elems:
            result = item.find(element)

            if result == None:
                pass

            else:
                # TODO: Make sure that if there is an already existing fingerprint that the newest one overrides the oldest.
                if element == "title":
                    fingerprint = __get_title_fingerprint(result.contents[0])
                    final_items[fingerprint] = {}

                try:
                    final_items[fingerprint][element] = result.contents[0]

                except:
                    pass

    return final_items
            

def __get_title_fingerprint(data: str) -> str:
    encoded_data = data.encode("utf-8")
    
    return str(hashlib.md5(encoded_data).hexdigest())
