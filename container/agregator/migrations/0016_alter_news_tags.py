# Generated by Django 4.0.5 on 2022-11-19 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agregator', '0015_remove_news_text_autor_news_text_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='tags',
            field=models.ManyToManyField(related_name='tegi', to='agregator.tag'),
        ),
    ]
