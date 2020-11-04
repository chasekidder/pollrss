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
import bs4.element

import hashlib


class FeedObj():
    """
    Database Feed Object

        Args:
            None

        Attributes:
            elements (Dict): Dictionary of feed element names and values.
            items (Dict): Dictionary of item dictionaries addressed by fingerprint.

        Functions:
            read_from_database(self, int) : Create Database Feed Object from Database Feed ID.

        Example:
            elements = {
                    "title": "Test Feed",
                    "description": "An Example Feed",
                    "link": "https://foo.bar"
                    }
            
            items = "1234567890": {
                                "title": "Example Item",
                                "link": "https://example.com/example-item"
                            },
                    "0987654321": {
                                "title": "Example Item 2",
                                "link": "https://example.com/example-item-2"
                            },
    """
    #TODO: Need a database variable to store css selector strings for html sources.


    feed_elements = [
                    "title",
                    "description",
                    "link",
                    "language",
                    "copyright",
                    "managingEditor",
                    "webMaster",
                    "pubDate",
                    "lastBuildDate",
                    "categories",
                    "generator",
                    "docs",
                    "cloud",
                    "ttl",
                    "image",
                    "rating",
                    "textInput",
                    "skipHours",
                    "skipDays",
                    "extensions"
                ]  
    

    item_elements = [
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


    path_elements = [
                    "feed_title",
                    "feed_description",
                    "feed_link",
                    "feed_language",
                    "feed_copyright",
                    "feed_pubDate",
                    "feed_lastBuildDate",
                    "feed_image",
                    "feed_rating",
                    "item_title",
                    "item_link",
                    "item_description",
                    "item_author",
                    "item_creator",
                    "item_comments",
                    "item_guid",
                    "item_pubDate",
                    "item_source"
                ]


    def __init__(self, elements = {}, items = {}, html_paths = None):
        self.elements = elements
        self.items = items
        self.html_paths = html_paths

    #TODO: Refactor create_from_html method 
    # -> Need a html_paths parameter
    @classmethod
    def create_from_html(cls, html: BeautifulSoup, link: str):
        """Create a FeedObj from html.

        Args:
            html (BeautifulSoup): Contains site html.

        Returns:
            FeedObj: Feed object containing all items and elements.
        """

        # Get Feed Elements
        elements = {
                    "title": None,
                    "link": None,
                    "description": None,
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

        title_path = ".hnname"
        description_path = ""
        link = link

        if title_path != "":
            title = cls.__get_elements_from_css_selector(title_path, html)[0]
            elements["title"] = title.string

        if description_path != "":
            description = cls.__get_elements_from_css_selector(description_path, html)[0]
            elements["description"] = description.string

        if link != "":
            elements["link"] = link

        # Get Feed Items
        items = {}
        table_path = "tr:is(.athing)"
        item_name_path = "a:is(.storylink)"


        table = cls.__get_elements_from_css_selector(table_path, html)
        
        for item in table:
            test = cls.__get_elements_from_css_selector(item_name_path, item)[0]

            items[cls.__get_title_fingerprint(test.string)] = {
                    "title": test.string,
                    "link": test["href"],
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

        return cls(elements, items)

    @classmethod
    def create_from_database(cls, feed_id: int):
        """Create FeedObj from Feed entry in database.

        Args:
            feed_id (int): Unique database feed identifier.

        Returns:
            FeedObj: Database feed object containing all items and elements.
        """
        elements = {}
        items = {}

        db_feed = Feed.objects.get(pk=feed_id)

        # Read feed elements
        for feed_field in db_feed.feedfield_set.all():
            elements[feed_field.name] = cls.__process_element(feed_field.value, feed_field.name)

        # Read all feed items
        for item in db_feed.item_set.all():
            items[item.fingerprint] = {}

            # Read all item elements
            # TODO: Limit query to 150ish items?
            for item_field in item.itemfield_set.all():
                items[item.fingerprint][item_field.name] = cls.__process_element(item_field.value, item_field.name)

        return cls(elements, items)

    @classmethod
    def create_from_rss_link(cls, link: str):
        """Create a FeedObj from an RSS link.

        Args:
            link (str): RSS feed source link.

        Returns:
            FeedObj: Feed object containing all items and elements.
        """
        elements = {}
        items = {}

        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.content, features='xml')
            rss_xml = soup.find("rss")
        
            if rss_xml == False:
                print("RSS Feed not found!")
                return 1

        except Exception as e:
            print("RSS Feed fetch FAILED! Error: " + e)
            return 1

        # Get Feed Elements
        for element in cls.feed_elements:
            value = rss_xml.find(element)

            if value is not None:
                try:
                    elements[element] = cls.__process_element(value.contents[0], element)

                except:
                    pass

        # Get Feed Items
        items_list = rss_xml.findAll("item")

        for item in items_list:
            for element in cls.item_elements:
                value = item.find(element)

                if value is not None:
                    # TODO: Make sure that if there is an already existing fingerprint that the newest one overrides the oldest.
                    try:
                        if element == "title":
                            fingerprint = cls.__get_title_fingerprint(value.contents[0])
                            items[fingerprint] = {}
                        items[fingerprint][element] = cls.__process_element(value.contents[0], element)

                    except:
                        pass

        return cls(elements, items)



    #TODO: Convert rss_link to source variable. Check/create a source fingerprint.
    def write_to_database(self, rss_link: str) -> int:
        """Write a feed object to the database and return the Feed ID.

        Args:
            rss_link (str): Source RSS feed link.

        Returns:
            int: New database Feed ID. (0 = Not Created)
        """

        feed = self
        source = "html"

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

                # Add css selector paths to database
                for path in feed.path_elements:
                    if feed.html_paths[path] is not None:
                        feed_path_field = FeedField(feed=db_feed)
                        feed_path_field.name = path
                        feed_path_field.value = feed.html_paths[path]
                        feed_path_field.required = False
                        feed_path_field.save()

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

    def view_feed(self) -> rfeed.Feed:
        """Generate an RSS Feed from a FeedObj.

        Args:
            feed_obj (FeedObj): Database feed object containing all items and elements.

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

        feed_obj = self

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
            rss_feed.items.append(self.__convert_to_rss_item(feed_obj.items[item]))

        return rss_feed

    
    def refresh_feed(self):
        #TODO: Implement feed refresh 
        # -> Create html or rss link FeedObj from source
        # -> Query fingerprints from database
        # -> Compare fingerprints 
        # -> Add new items to database
        pass


    @staticmethod
    def __get_elements_from_css_selector(css_selector: str, html: BeautifulSoup):
        return html.select(css_selector)

    @staticmethod
    def __process_element(value: str, name: str):
        """Process RSS element into appropriate format for rfeed.

        Args:
            value (str): Element value.

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

    @staticmethod
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

    @staticmethod
    def __get_title_fingerprint(data: str) -> str:
        encoded_data = data.encode("utf-8")
        
        return str(hashlib.md5(encoded_data).hexdigest())

    @staticmethod
    def __get_xpath_from_soup(html_element) -> str:
        """ *NOT USED*
        Create an xpath from a BeautifulSoup html element.

        Args:
            html (BeautifulSoup element): HTML element.

        Returns:
            str: Unique xpath string.
        """

        # Heavy inspiration from: Felipe A Hernandez
        # < https://gist.github.com/ergoithz/6cf043e3fdedd1b94fcf >

        components = []
        child = html_element if html_element.name else html_element.parent

        for parent in child.parents:
            siblings = parent.find_all(child.name, recursive=False)

            components.append(child.name if 1 == len(siblings) else '%s[%d]' % ( child.name,
                    next(i for i, sibling in enumerate(siblings, 1) if sibling is child)
                    )
                )

            child = parent

        components.reverse()
        xpath = '/%s' % '/'.join(components)

        return xpath


        element = html.select(css_selector)

        return element

    @staticmethod
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



