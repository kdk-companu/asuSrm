from django.db import models
from transliterate.utils import _

from apps.workers.models import UserBasic


class CustomerManager(models.Manager):
    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError(_('Не указан телефонный номер.'))
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=UserBasic.Types.CUSTOMER)


class Customer(UserBasic):
    class Meta:
        proxy = True

    objects = CustomerManager()

    def save(self, *args, **kwargs):
        self.type = UserBasic.Types.CUSTOMER
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь. Заказчик.'
        verbose_name_plural = 'Пользователь. Заказчики.'
        ordering = ['pk']
        default_permissions = ('')

        permissions = (
            ('UserCustomer_add', 'Пользователь. Заказчик. Добавить.'),
            ('UserCustomer_change', 'Пользователь. Заказчик. Редактировать.'),
            ('UserCustomer_delete', 'Пользователь. Заказчик. Удалить.'),
            ('UserCustomer_view', 'Пользователь. Заказчик. Просмотреть.'),
        )
