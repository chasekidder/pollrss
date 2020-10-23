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

from django.db import models

# Create your models here.

class Feed(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField()

    def __str__(self):
        return str(self.id)

class FeedField(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    required = models.BooleanField(default=True)
    value = models.CharField(max_length=2000)

    def __str__(self):
        return str(self.feed.id) + " - " + self.name

class Item(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    fingerprint = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return str(self.feed.id) + " - " + str(self.id)

class ItemField(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    required = models.BooleanField(default=True)
    value = models.CharField(max_length=2000)

    def __str__(self):
        return str(self.item.id) + " - " + self.name


