from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
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
        default_permissions = ('')
        permissions = (
            ('subdivision_add', 'Управление/Подразделение. Добавить.'),
            ('subdivision_change', 'Управление/Подразделение. Редактировать.'),
            ('subdivision_delete', 'Управление/Подразделение. Удалить.'),
            ('subdivision_view', 'Управление/Подразделение. Просмотреть.'),
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
        default_permissions = ('')
        permissions = (
            ('department_add', 'Отдел. Добавить.'),
            ('department_change', 'Отдел. Редактировать.'),
            ('department_delete', 'Отдел. Удалить.'),
            ('department_view', 'Отдел. Просмотреть.'),
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
        ordering = ['-rights']
        default_permissions = ('')
        permissions = (
            ('chief_add', 'Должность. Добавить.'),
            ('chief_change', 'Должность. Редактировать.'),
            ('chief_delete', 'Должность. Удалить.'),
            ('chief_view', 'Должность. Просмотреть.'),
            ('chief_permissions', 'Должность. Права должности.'),
        )


@receiver(post_save, sender=Chief)
def post_save_receiver(sender, instance, created, raw, using, **kwargs):
    if created:
        group_save = Group.objects.create(name=instance.name)
        Chief.objects.filter(id=instance.pk).update(group=group_save)
    else:
        Group.objects.filter(id=instance.group.pk).update(name=instance.name)


@receiver(post_delete)
def post_delete_receiver(sender, instance, using, **kwargs):
    try:
        remove = Group.objects.filter(id=instance.group.pk)
        remove.delete()
    except Exception:
        pass
