from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import News, Category
from .models import Tag
from django import forms


class NewsAdminForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content_url', 'category', 'published_at', 'tags']


class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ('id', 'title', 'content_url', 'category', 'published_at')
    list_display_links = ('title', )
    search_fields = ('title',)
    list_editable = ('category', )
    list_filter = ('category', )
    fields = ('title', 'content_url', 'category', 'published_at', 'tags')
    save_on_top = True


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('title', )


admin.site.register(News, NewsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag)
admin.site.site_title = "Кабинет администратора"
admin.site.site_header = "Кабинет администратора"