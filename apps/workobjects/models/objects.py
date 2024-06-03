from django.db import models
from transliterate import translit
from django.template.defaultfilters import slugify

from apps.workers.models.user_exploitation import OrganizationExploitation


class OrganizationsObjects(models.Model):
    """Объекты"""
    organization = models.ForeignKey(OrganizationExploitation, on_delete=models.CASCADE,
                                     verbose_name='Эксплуатирующая организация')
    name = models.CharField(max_length=255, unique=True, verbose_name='Название объекта')
    name_tables = models.CharField(max_length=80, unique=False, blank=True, verbose_name='Название для табеля')
    short_names = models.CharField(max_length=80, unique=False, blank=True, verbose_name='Обиходные название')
    city = models.CharField(max_length=80, unique=False, blank=True, verbose_name='Ближайший город')
    property_location = models.TextField(verbose_name='Расположение объекта. Транспорт.', blank=True)
    pay_weekend = models.BooleanField(default=False, verbose_name='Оплата выходных')
    pay_processing = models.BooleanField(default=False, verbose_name='Оплата переработки')
    description = models.TextField(verbose_name='Описание объекта', blank=True)

    slug = models.SlugField(max_length=150, unique=True, db_index=True,
                            verbose_name='URL')

    def __str__(self):
        return self.organization.name + ". " + self.name

    def save(self, **kwargs):
        self.slug = slugify(translit(str(self.name), 'ru', reversed=True))
        super(OrganizationsObjects, self).save()

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'
        ordering = ['organization']
        default_permissions = ('')
        permissions = (
            ('organizationsObjects_add', 'Объекты. Добавить.'),
            ('organizationsObjects_view', 'Объекты. Просмотреть.'),
            ('organizationsObjects_delete', 'Объекты. Удалить.'),
            ('organizationsObjects_change', 'Объекты. Редактировать.'),
        )
