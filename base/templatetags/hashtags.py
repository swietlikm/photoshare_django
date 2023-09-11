from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def hashtag(value):
    def repl(match):
        hashtag = match.group(1)
        url = reverse('explore_tags', args=[hashtag[1:]])
        return f'<a href="{url}" class="text-decoration-none">{hashtag}</a>'

    pattern = r'(#\w+)'
    result = re.sub(pattern, repl, value)

    return mark_safe(result)
