from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.urls import reverse

from .models import Feed, Field, FeedField
from .forms import IndexForm

import requests
import urllib
from base64 import b64encode

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
