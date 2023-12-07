from django.db import models
from django.urls import reverse
from transliterate import translit
from django.template.defaultfilters import slugify
from django.contrib.auth.models import Group


class Subdivision(models.Model):
    """Описания управлений"""
    name = models.CharField(max_length=150, unique=True, verbose_name='Управление/Подразделение')
    abbreviation = models.CharField(max_length=100, unique=True, verbose_name='Сокращенное название')
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание')  # blank=True Пустое имя поля
    slug = models.SlugField(max_length=100, unique=True, db_index=True,
                            verbose_name='URL')  # unique - Уникальное,db_index - индексируемое

    def __str__(self):
        return '{0}({1})'.format(self.name, self.abbreviation)

    def get_absolute_url(self):
        return reverse('subdivision', kwargs={'subdivision_slug': self.slug})

    def save(self, **kwargs):
        self.slug = slugify(translit(self.abbreviation, 'ru', reversed=True))
        super(Subdivision, self).save()

    # Админка на русском языке
    class Meta:
        verbose_name = 'Управление/Подразделение'
        verbose_name_plural = 'Управления/Подразделения'
        ordering = ['pk']
        permissions = (
            ('subdivision_add', 'Добавить.'),
            ('subdivision_change', 'Редактировать.'),
            ('subdivision_delete', 'Удалить.'),
            ('subdivision_view', 'Просмотреть.'),
        )


class Department(models.Model):
    """Описание отдела"""
    name = models.CharField(max_length=150, unique=True, verbose_name='Отдел')
    abbreviation = models.CharField(max_length=100, unique=True, verbose_name='Сокращенное название')
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание')
    slug = models.SlugField(max_length=100, unique=True, db_index=True,
                            verbose_name='URL')  # unique - Уникальное,db_index - индексируемое

    def __str__(self):
        return '{0}({1})'.format(self.name, self.abbreviation)

    def get_absolute_url(self):
        return reverse('department', kwargs={'department_slug': self.slug})

    def save(self, **kwargs):
        self.slug = slugify(translit(self.abbreviation, 'ru', reversed=True))
        super(Department, self).save()

    class Meta:
        verbose_name = 'Структура/Отдел'
        verbose_name_plural = 'Структура/Отделы'
        ordering = ['pk']
        permissions = (
            ('department_add', 'Добавить.'),
            ('department_change', 'Редактировать.'),
            ('department_delete', 'Удалить.'),
            ('department_view', 'Просмотреть.'),
        )


class Chief(models.Model):
    """Описание должностей."""
    name = models.CharField(max_length=150, unique=True, verbose_name='Должность')
    abbreviation = models.CharField(max_length=100, unique=True, verbose_name='Сокращенное название')
    rights = models.IntegerField(default=0, unique=True, verbose_name='Уровень доступа')
    slug = models.SlugField(max_length=100, unique=True, db_index=True,
                            verbose_name='URL')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, blank=True,
                              null=True, verbose_name='Группы')  # Ссылка на стандартные группы

    def __str__(self):
        return '{0}({1})'.format(self.name, self.abbreviation)

    def get_absolute_url(self):
        return reverse('chief', kwargs={'chief_slug': self.slug})

    def save(self, **kwargs):
        self.slug = slugify(translit(self.abbreviation, 'ru', reversed=True))
        super(Chief, self).save()

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['rights']
        permissions = (
            ('chief_add', 'Добавить.'),
            ('chief_change', 'Редактировать.'),
            ('chief_delete', 'Удалить.'),
            ('chief_view', 'Просмотреть.'),
        )
