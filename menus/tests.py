from django.test import RequestFactory, TestCase

from .models import Menu, MenuItem
from .services import MenuContextBuilder, fetch_menu_items


class MenuBuilderTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.menu = Menu.objects.create(title="Test menu", slug="test_menu")
        self.root_home = MenuItem.objects.create(
            menu=self.menu,
            title="Главная",
            named_url="home",
            order=1,
        )
        self.root_docs = MenuItem.objects.create(
            menu=self.menu,
            title="Документация",
            url="/docs/",
            order=2,
        )
        self.level_two = MenuItem.objects.create(
            menu=self.menu,
            parent=self.root_docs,
            title="API",
            url="/docs/api/",
            order=1,
        )
        self.level_three = MenuItem.objects.create(
            menu=self.menu,
            parent=self.level_two,
            title="v1",
            url="/docs/api/v1/",
            order=1,
        )
        self.root_contacts = MenuItem.objects.create(
            menu=self.menu,
            title="Контакты",
            named_url="contacts",
            order=3,
        )

    def test_fetch_menu_items_one_query_with_request_cache(self) -> None:
        request = self.factory.get("/")
        with self.assertNumQueries(1):
            first = fetch_menu_items(self.menu.slug, request=request)
            second = fetch_menu_items(self.menu.slug, request=request)
        self.assertEqual(len(first), len(second))

    def test_builder_marks_active_and_expands_branch(self) -> None:
        request = self.factory.get("/docs/api/")
        builder = MenuContextBuilder(self.menu.slug, request=request)
        menu = builder.build()

        nodes = menu["nodes"]
        docs_node = next(node for node in nodes if node["title"] == "Документация")
        self.assertTrue(docs_node["is_ancestor"])
        self.assertTrue(docs_node["show_children"])

        api_node = docs_node["children"][0]
        self.assertTrue(api_node["is_active"])
        self.assertTrue(api_node["show_children"], "Активный пункт должен раскрывать детей")
        self.assertEqual(api_node["children"][0]["title"], "v1")

    def test_builder_uses_single_query(self) -> None:
        request = self.factory.get("/")
        with self.assertNumQueries(1):
            MenuContextBuilder(self.menu.slug, request=request).build()
