# Generated by Django 4.0.5 on 2022-06-15 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agregator', '0013_alter_category_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='preview_text',
            field=models.TextField(default=None, verbose_name='Текст новости'),
        ),
    ]
