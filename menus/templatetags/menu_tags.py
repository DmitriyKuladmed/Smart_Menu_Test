from __future__ import annotations

from typing import Any, Dict

from django import template
from django.http import HttpRequest

from ..services import MenuContextBuilder

register = template.Library()


@register.inclusion_tag("menus/menu.html", takes_context=True)
def draw_menu(context: Dict[str, Any], menu_slug: str) -> Dict[str, Any]:
    """
    Template-tag: {% draw_menu 'main_menu' %}
    """

    request: HttpRequest | None = context.get("request")
    builder = MenuContextBuilder(menu_slug=menu_slug, request=request)
    return {"menu": builder.build()}

