from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Menu(models.Model):
    """Отдельный набор пунктов меню, доступный по уникальному слагу."""

    title = models.CharField("Название меню", max_length=150)
    slug = models.SlugField("Слаг", max_length=50, unique=True)

    class Meta:
        verbose_name = "Меню"
        verbose_name_plural = "Меню"
        ordering = ("title",)

    def __str__(self) -> str:
        return self.title


class MenuItem(models.Model):
    """Пункт меню с поддержкой вложенности и двух типов ссылок."""

    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Меню",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
        verbose_name="Родительский пункт",
    )
    title = models.CharField("Заголовок", max_length=200)
    named_url = models.CharField(
        "Named URL",
        max_length=200,
        blank=True,
        help_text="Имя маршрута из urls.py (reverse).",
    )
    url = models.CharField(
        "Явный URL",
        max_length=300,
        blank=True,
        help_text="Полный путь, если не используется named URL.",
    )
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"
        ordering = ("menu", "parent__id", "order", "id")

    def __str__(self) -> str:
        return f"{self.menu.slug}: {self.title}"

    def clean(self) -> None:
        """Валидируем, что указан хотя бы один вид ссылки."""
        if not (self.named_url or self.url):
            raise ValidationError("Необходимо указать named_url или явный url.")
        if self.named_url and self.url:
            raise ValidationError("Укажите только один тип ссылки.")
        super().clean()

    def get_link(self) -> str:
        """Возвращает итоговый URL для использования в шаблонах."""
        if self.named_url:
            return reverse(self.named_url)
        return self.url

    @property
    def has_children(self) -> bool:
        return self.children.exists()
