from django import template
from django.core.cache import cache
from agregator.models import Category

register = template.Library()


@register.inclusion_tag('agregator/list_categories.html')
def show_categories():
    categories = cache.get_or_set('categories', Category.objects.all(), 15)
    return {'categories': categories}
