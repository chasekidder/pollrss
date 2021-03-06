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

from django import forms

FEEDS = (
    ("1", "Feed1"),
    ("2", "Feed2"),
    ("3", "Feed3")

)

class IndexForm(forms.Form):
    url = forms.CharField(max_length=2000, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'https://'}))

class FeedForm(forms.Form):
    feed = forms.ChoiceField(choices=FEEDS)