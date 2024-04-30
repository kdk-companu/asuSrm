from django.db import models
from transliterate.utils import _

from apps.workers.models import UserBasic


class WatcherManager(models.Manager):
    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError(_('Не указан телефонный номер.'))
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=UserBasic.Types.WATCHER)


class Watcher(UserBasic):
    class Meta:
        proxy = True

    objects = WatcherManager()

    def save(self, *args, **kwargs):
        self.type = UserBasic.Types.WATCHER
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь. Наблюдатель.'
        verbose_name_plural = 'Пользователи. Наблюдатели.'
        ordering = ['pk']
        default_permissions = ('')

        permissions = (
            ('UserWatcher_add', 'Пользователи. Наблюдатель. Добавить.'),
            ('UserWatcher_change', 'Пользователи. Наблюдатель. Редактировать.'),
            ('UserWatcher_delete', 'Пользователи. Наблюдатель. Удалить.'),
            ('UserWatcher_view', 'Пользователи. Наблюдатель. Просмотреть.'),
        )