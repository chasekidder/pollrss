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

    print (rss_feed.pubDate)

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


#TODO: Need function that updates existing feeds in the database. Eg. check new feed against database fingerprints and only add new ones.


def write_feed_to_database(url: str):
    """Fetch an RSS feed from URL and write it to a new feed in the database.

    Args:
        url (str): Source RSS feed URL.

    Returns:
        int: New database Feed ID. (0 = Not Created)
    """

    feed = fetch_feed_from_url(url)

    print("Feed Exists: " + str(__feed_exists(url)))

    # Check for feed existence
    if (__feed_exists(url)):
        print("Feed Already Exists!")

    else:

        # Start a bulk database transaction
        with transaction.atomic():

            # Create a new feed entry in database
            db_feed = Feed()
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


def __feed_exists(url: str) -> bool:

    try:
        feeds = Feed.objects.get(feedfield__value__exact=url)
    except Feed.DoesNotExist:
        return False

    return True

    
def fetch_feed_from_url(url: str):

    try:
        response = requests.get(url)

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
                elements[element] = r.contents
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
                    item_dict = {element: result.contents[0]}
                    final_items[fingerprint][element] = item_dict

                except:
                    pass

    return final_items
            

def __get_title_fingerprint(data: str) -> str:
    encoded_data = data.encode("utf-8")
    
    return str(hashlib.md5(encoded_data).hexdigest())
