from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def current_url_name(context):
    match = context["request"].resolver_match
    if match.namespace:
        return f"{match.namespace}:{match.url_name}"
    return match.url_name
