# Generated by Django 4.0.5 on 2022-06-11 19:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agregator', '0008_news_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='tags',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]