from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlsplit

from django.http import HttpRequest
from django.urls import NoReverseMatch

from .models import MenuItem

_REQUEST_CACHE_ATTR = "_menu_cache"


def _ensure_request_cache(request: Optional[HttpRequest]) -> Optional[Dict[str, List[MenuItem]]]:
    if request is None:
        return None
    cache: Optional[Dict[str, List[MenuItem]]] = getattr(request, _REQUEST_CACHE_ATTR, None)
    if cache is None:
        cache = {}
        setattr(request, _REQUEST_CACHE_ATTR, cache)
    return cache


def fetch_menu_items(menu_slug: str, request: Optional[HttpRequest] = None) -> List[MenuItem]:
    """
    Возвращает все пункты меню за один SQL-запрос, кешируя результат на время запроса.
    """

    cache = _ensure_request_cache(request)
    if cache is not None and menu_slug in cache:
        return cache[menu_slug]

    items = list(
        MenuItem.objects.filter(menu__slug=menu_slug)
        .select_related("menu", "parent")
        .order_by("parent_id", "order", "id")
    )

    if cache is not None:
        cache[menu_slug] = items

    return items


class MenuContextBuilder:
    """Готовит структуру данных для шаблона draw_menu."""

    def __init__(self, menu_slug: str, request: Optional[HttpRequest] = None):
        self.menu_slug = menu_slug
        self.request = request
        self.items: List[MenuItem] = fetch_menu_items(menu_slug, request)
        self._items_by_id: Dict[int, MenuItem] = {item.id: item for item in self.items}
        self._children_map: Dict[Optional[int], List[MenuItem]] = defaultdict(list)
        for item in self.items:
            self._children_map[item.parent_id].append(item)
        for children in self._children_map.values():
            children.sort(key=lambda x: (x.order, x.id))

        self._urls: Dict[int, str] = self._build_url_map()
        self._active_item_id: Optional[int] = self._detect_active_item_id()
        self._ancestor_ids: Set[int] = self._collect_ancestor_ids()

    def build(self) -> Dict[str, Any]:
        return {
            "slug": self.menu_slug,
            "title": self._resolve_menu_title(),
            "nodes": self._build_nodes(parent_id=None),
        }

    def _resolve_menu_title(self) -> str:
        if self.items:
            return self.items[0].menu.title
        return self.menu_slug

    def _build_nodes(self, parent_id: Optional[int]) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        for item in self._children_map.get(parent_id, []):
            node_id = item.id
            show_children = self._should_expand(node_id)
            child_nodes = self._build_nodes(node_id) if show_children else []
            nodes.append(
                {
                    "id": node_id,
                    "title": item.title,
                    "url": self._urls.get(node_id, "#"),
                    "is_active": node_id == self._active_item_id,
                    "is_ancestor": node_id in self._ancestor_ids,
                    "show_children": show_children,
                    "has_children": bool(self._children_map.get(node_id)),
                    "children": child_nodes,
                }
            )
        return nodes

    def _build_url_map(self) -> Dict[int, str]:
        url_map: Dict[int, str] = {}
        for item in self.items:
            try:
                url_map[item.id] = item.get_link()
            except NoReverseMatch:
                # Повторно пробрасываем исключение, чтобы разработчик увидел неверный named url
                raise
        return url_map

    def _detect_active_item_id(self) -> Optional[int]:
        if not self.request:
            return None
        current_path = _normalize_path(self.request.path)
        for item_id, url in self._urls.items():
            if _normalize_path(url) == current_path:
                return item_id
        return None

    def _collect_ancestor_ids(self) -> Set[int]:
        if not self._active_item_id:
            return set()
        ancestors: Set[int] = set()
        parent_id = self._items_by_id[self._active_item_id].parent_id
        while parent_id:
            ancestors.add(parent_id)
            parent = self._items_by_id.get(parent_id)
            if parent is None:
                break
            parent_id = parent.parent_id
        return ancestors

    def _should_expand(self, item_id: int) -> bool:
        if self._active_item_id is None:
            return False
        return item_id == self._active_item_id or item_id in self._ancestor_ids


def _normalize_path(value: Optional[str]) -> str:
    if not value:
        return "/"
    parsed = urlsplit(value)
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return path

