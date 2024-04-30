import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from transliterate import translit
from django.template.defaultfilters import slugify
from django.utils import timezone
from transliterate.utils import _

from library.image import ImagesEdit


class UserBasicManager(BaseUserManager):
    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError(_('Не указан телефонный номер.'))
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(phone, password, **extra_fields)


def user_path(instance, filename):
    return 'user/{0}/images/{1}'.format(instance.pk, filename)


class UserBasic(AbstractBaseUser, PermissionsMixin):
    class Types(models.TextChoices):
        WORKER = "WORKER", "Сотрудник"  #
        WATCHER = "WATCHER", "Наблюдатель"  #
        EXPLOITATION = "EXPLOITATION", "Эксплуатация"  #
        CUSTOMER = "CUSTOMER", "Заказчик"
        SERVICEMAN = "SERVICEMAN", "Наладчик"

    # ФИО
    surname = models.CharField(max_length=60, unique=False, verbose_name='Фамилия')
    name = models.CharField(max_length=60, unique=False, verbose_name='Имя')
    patronymic = models.CharField(max_length=60, unique=False, verbose_name='Отчество')
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name='slug')
    # Контакты
    phone = PhoneNumberField(null=False, blank=False, unique=True, verbose_name='Телефон')
    email = models.EmailField(unique=False, verbose_name='Почта')
    # Аватарки
    image = models.ImageField(upload_to=user_path, null=True, blank=True, verbose_name='Аватарка')
    image_smol = models.ImageField(upload_to=user_path, null=True, blank=True, verbose_name='Аватарка маленькая')

    type = models.CharField(max_length=13, choices=Types.choices,
                            default=Types.WATCHER, verbose_name='Тип пользователя')
    # Система прав
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['surname', 'name', 'patronymic']

    # defining the manager for the UserAccount model
    objects = UserBasicManager()

    def __str__(self):
        return '{0} {1} {2}'.format(self.surname, self.name, self.patronymic)

    def save(self, *args, **kwargs):
        if not self.type or self.type == None:
            self.type = UserBasic.Types.WATCHER
        if not self.slug:
            # Проверить на повторение slug
            try:
                UserBasic.objects.get(slug="{0}{1}{2}".format(self.surname, self.name, self.patronymic))
                date_add = datetime.date.today().strftime("%d-%m-%Y")
                slug_name = "{0}{1}{2}".format(self.surname, self.name, self.patronymic, date_add)
            except UserBasic.DoesNotExist:
                slug_name = "{0}{1}{2}".format(self.surname, self.name, self.patronymic)
            self.slug = slugify(translit(slug_name, 'ru', reversed=True))
        # Сохранение фотографий
        if self.image:

            # Полный путь к папкам
            image = ImagesEdit.add_avatar(self.image, str(self.pk))
            self.image = image['image']
            self.image_smol = image['images_smol']

        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь. Базовая.'
        verbose_name_plural = 'Пользователи. Базовая.'
        ordering = ['pk']
        default_permissions = ('')

        permissions = (
            ('UserBasic_permission', 'Пользователи. Права доступа.'),
        )
