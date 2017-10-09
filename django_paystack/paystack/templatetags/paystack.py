import datetime
from django import template
from django.utils.html import format_html
register = template.Library()


@register.inclusion_tag('paystack_button.html', takes_context=True)
def paystack_button(context, form):
    return {}
