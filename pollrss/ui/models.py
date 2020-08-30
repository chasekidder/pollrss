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
    uri = models.CharField(max_length=2000)
    xpath = models.CharField(max_length=2000)
    edited = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class Field(models.Model):
    name = models.CharField(max_length=200)
    required = models.BooleanField(default=True)

class FeedField(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    xpath = models.CharField(max_length=2000)

class Post(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    md5sum = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = ['feed', 'md5sum']
