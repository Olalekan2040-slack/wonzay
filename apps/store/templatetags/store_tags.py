from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def split(value, arg):
    """Split a string by arg. Usage: "a,b,c"|split:"," """
    return str(value).split(arg)


@register.filter
def strip(value):
    """Strip whitespace from a string."""
    return str(value).strip()


@register.filter
def star_range(value):
    """Return range(1,6) for use in star rating loops."""
    try:
        return range(1, 6)
    except Exception:
        return range(1, 6)


@register.filter
def filled_stars(rating, max_stars=5):
    """Return list of booleans: True=filled, False=empty."""
    try:
        r = round(float(rating))
        return [i <= r for i in range(1, int(max_stars) + 1)]
    except Exception:
        return [False] * 5


@register.filter
def currency_aud(value):
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return f"${value}"


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def active_class(request, url_name):
    from django.urls import resolve, Resolver404
    try:
        match = resolve(request.path_info)
        if match.url_name == url_name:
            return "text-[var(--color-primary)]"
    except Resolver404:
        pass
    return ""
