# Generated by Django 4.0.5 on 2022-11-19 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agregator', '0016_alter_news_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tagarticle',
            field=models.CharField(max_length=50, verbose_name='Тег'),
        ),
    ]
