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

from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.urls import reverse

from .models import Feed, Field, FeedField
from .forms import IndexForm, FeedForm
from .rfeed import *

import requests
import urllib
from base64 import b64encode
from bs4 import BeautifulSoup

# Serve the index page and get url
def index(request):
    if request.method == 'GET' and 'url' in request.GET:
        form = IndexForm(request.GET)
        if form.is_valid():
            val = URLValidator()
            try:
                url = request.GET['url']
                if not url.startswith('https'):
                    url = 'https://' + url
                val(url)
            except ValidationError:
                form.add_error('url', 'Invalid url')
            else:
                return HttpResponseRedirect('/create?url=%s' % urllib.parse.quote(url.encode('utf8')))
    else:
        form = IndexForm()

    return render(request, 'ui/index.html', {'form': form})

@ensure_csrf_cookie
def create(request):
    if request.method == 'GET' and 'url' in request.GET:
        ext_page_url = request.GET['url']

        r = requests.get(ext_page_url)

        b64_html = b64encode(r.content.decode(r.encoding).encode("utf-8"))

        return render(request, 'ui/create.html',
                        {
                            'b64_html': b64_html.decode("utf-8"),
                            'ext_page_url': ext_page_url
                        })

    return HttpResponseBadRequest('Url is required')

def feeds(request):
    if request.method == 'GET' and 'feed' in request.GET:
        form = FeedForm(request.GET)
        if form.is_valid():
            feed = request.GET['feed']

            return HttpResponseRedirect('/feed?feed=%s' % feed)

    else:
        form = FeedForm()

    return render(request, 'ui/feeds.html', {'form': form})

@ensure_csrf_cookie
def feed(request):
    if request.method == 'GET' and 'feed' in request.GET:
        feed_id = request.GET['feed']

        import datetime

        test_item1 = Item(
            title = "First article",
            link = "http://www.example.com/articles/1", 
            description = "This is the description of the first article",
            author = "Santiago L. Valdarrama",
            guid = Guid("http://www.example.com/articles/1"),
            pubDate = datetime.datetime(2014, 12, 29, 10, 00)
            )   

        test_item2 = Item(
            title = "Second article",
            link = "http://www.example.com/articles/2", 
            description = "This is the description of the second article",
            author = "Santiago L. Valdarrama",
            guid = Guid("http://www.example.com/articles/2"),
            pubDate = datetime.datetime(2014, 12, 30, 14, 15)
            )

        

        feed = Feed(
            title = "Sample RSS Feed",
            link = "http://www.example.com/rss",
            description = r"""<script xmlns="http://www.w3.org/1999/xhtml"><![CDATA[alert('Hello');]]></script>""",
            language = "en-US",
            lastBuildDate = datetime.datetime.now(),
            items = [test_item1, test_item2]
            )

        soup = BeautifulSoup(feed.rss(), "xml")
        pretty_xml = soup.prettify()

        pretty_xml = pretty_xml

        b64_xml = b64encode(pretty_xml.encode('utf-8'))

        return render(request, 'ui/feed.html',
                        {
                            'feed_name': "Test Feed",
                            'feed_xml': b64_xml.decode("utf-8")
                        })

    return HttpResponseBadRequest('Feed is required')