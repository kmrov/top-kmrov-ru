from django.template.defaultfilters import stringfilter

from django import template
register = template.Library()

import re

@register.filter
@stringfilter
def cut_entry(value):
    try:
        text = re.match('(?P<txt>(.*?<br>){1,4})', value).group("txt")
    except:
        text = value
    if len(text)>380:
        text = text[:380]
        try:
            text = re.match('(?s)(.*)\s', text).group(0)
        except:
            pass
    if text.endswith("<br>"):
        text = text[:-4]
    return text

@register.filter
@stringfilter
def clean_url(value):
    new_link = value.replace("http://", '')
    if new_link.endswith("/"):
        new_link = new_link[:-1]
    return new_link
