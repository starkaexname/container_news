# Generated by Django 4.0.5 on 2022-06-11 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agregator', '0005_remove_news_preview_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='photo_url',
            field=models.DateTimeField(default=None, verbose_name='Ссылка на фото'),
        ),
    ]
