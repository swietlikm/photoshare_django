from django import template

register = template.Library()

@register.filter
def hashtag(value):
    return value.upper()