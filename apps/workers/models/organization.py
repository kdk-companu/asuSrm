from django.db import models
from transliterate import translit
from django.template.defaultfilters import slugify


class Organization_Direction(models.Model):
    """Направление деятельности организации"""
    name = models.CharField(max_length=255, unique=True, verbose_name='Направление деятельности')
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name='URL')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Направление деятельности'
        verbose_name_plural = 'Направление деятельности'
        ordering = ['name']

    def save(self, **kwargs):
        self.slug = slugify(translit(self.name, 'ru', reversed=True))
        super(Organization_Direction, self).save()


class Organization(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Название')
    organization_direction = models.ForeignKey(Organization_Direction, on_delete=models.PROTECT, blank=False, null=True,
                                               verbose_name='Направление деятельности')
    inn = models.CharField(max_length=150, blank=True, unique=True, verbose_name='ИНН')
    website = models.CharField(max_length=150, blank=True, unique=True, verbose_name='Сайт')
    description = models.TextField(verbose_name='Описание', blank=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name='URL')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        ordering = ['pk']

    def save(self, **kwargs):
        self.slug = slugify(translit(self.name, 'ru', reversed=True))
        super(Organization, self).save()
