# Generated by Django 4.0.5 on 2022-12-08 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agregator', '0017_alter_tag_tagarticle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='photo_src_name',
            field=models.CharField(default=None, max_length=100, verbose_name='Источник фото'),
        ),
        migrations.AlterField(
            model_name='news',
            name='text_author',
            field=models.CharField(default=None, max_length=100, verbose_name='Автор текста'),
        ),
    ]
