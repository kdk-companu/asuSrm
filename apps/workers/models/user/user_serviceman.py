from django.db import models
from transliterate.utils import _

from apps.workers.models import UserBasic


class ServicemanManager(models.Manager):
    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError(_('Не указан телефонный номер.'))
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=UserBasic.Types.SERVICEMAN)


class Serviceman(UserBasic):
    class Meta:
        proxy = True

    objects = ServicemanManager()

    def save(self, *args, **kwargs):
        self.type = UserBasic.Types.SERVICEMAN
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь. Наладчик.'
        verbose_name_plural = 'Пользователи. Наладчики.'
        ordering = ['pk']
        default_permissions = ('')

        permissions = (
            ('UserServiceman_add', 'Пользователи. Наладчики. Добавить.'),
            ('UserServiceman_change', 'Пользователи. Наладчики. Редактировать.'),
            ('UserServiceman_delete', 'Пользователи. Наладчики. Удалить.'),
            ('UserServiceman_view', 'Пользователи. Наладчики. Просмотреть.'),
        )