# Generated by Django 3.1 on 2020-10-23 19:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0003_auto_20200830_2137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feed',
            name='url',
        ),
    ]
