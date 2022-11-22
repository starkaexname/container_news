from django.db import models
from django.urls import reverse


class Tag(models.Model):
    tagarticle = models.CharField(max_length=50, verbose_name='Тег')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['tagarticle']

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_id': self.pk})

    def __str__(self):
        return self.tagarticle


class News(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название новости')
    content_url = models.URLField(verbose_name='Ссылка на новость', default=None)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория')
    full_text = models.TextField('Текст новости', default=None)
    preview_text = models.TextField('Текст новости', default=None)
    text_author = models.CharField(max_length=50, verbose_name='Автор текста', default=None)
    published_at = models.DateTimeField(verbose_name='Дата публикации', default=None)
    photo_url = models.URLField(verbose_name='Ссылка на фото', default=None)
    photo_src_name = models.CharField(max_length=50, verbose_name='Источник фото', default=None)
    views = models.PositiveIntegerField(verbose_name='Просмотры', default=None)
    tags = models.ManyToManyField('Tag', related_name='tegi')

    def get_absolute_url(self):
        return reverse('view_news', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']


class Category(models.Model):
    title = models.CharField(max_length=150, db_index=True, verbose_name='Наименование категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['pk']

    def get_absolute_url(self):
        return reverse('cat', kwargs={'category_id': self.pk})

    def __str__(self):
        return self.title
