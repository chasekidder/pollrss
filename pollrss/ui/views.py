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
from django.views import generic

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.urls import reverse

from .models import Feed, FeedField, Item, ItemField
from .forms import IndexForm, FeedForm
from . import rss

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
                return HttpResponseRedirect('/create/?url=%s' % urllib.parse.quote(url.encode('utf8')))
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


class FeedListView(generic.ListView):
	model = Feed


@ensure_csrf_cookie
def viewfeed(request, feed_id):
    if request.method == 'GET':

        rss_feed = rss.create_rss_feed_from_object(feed_id)
        
        soup = BeautifulSoup(rss_feed.rss(), "xml")
        
        pretty_xml = soup.prettify()

        b64_xml = b64encode(pretty_xml.encode('utf-8'))

        context = {
                    'feed_name': rss_feed.title,
                    'feed_xml': b64_xml.decode("utf-8")
                }

        return render(request, 'ui/feed.html', context=context)

    return HttpResponseBadRequest('Feed is required')



@ensure_csrf_cookie
def feed(request, feed_id):
    if request.method == 'GET':

        rss_feed = rss.create_rss_feed_from_object(feed_id).rss()

        return HttpResponse(rss_feed, content_type='application/rss+xml')
        #return render(request, "ui/feed.xml", context)

    return HttpResponseBadRequest('Feed is required')



@ensure_csrf_cookie
def test(request):
    if request.method == 'GET':
        url = "http://rss.cnn.com/rss/cnn_topstories.rss"
        #print("result: " + str(rss.write_feed_to_database(rss.fetch_feed_from_link(url), url))) 
        return HttpResponseRedirect('/viewfeed/%s' % str(rss.write_feed_to_database(rss.read_feed_from_link(url), url)))
        #return HttpResponseBadRequest('RSS Feed Fetched')