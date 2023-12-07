from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from apps.workers.models import Department, Subdivision, Chief, User
from django.utils.translation import gettext_lazy as _



admin.site.register(Subdivision)
admin.site.register(Department)
admin.site.register(Chief)



class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    model = User
    list_display = ('surname', 'name', 'patronymic', 'phone',  'is_staff', 'is_active',)
    list_filter = ('employee', 'is_staff', 'is_active',)
    list_display_links = ('surname', 'name', 'patronymic', 'phone')

    fieldsets = (
        (_('Personal info'), {'fields': (
            'surname', 'name', 'patronymic')}),
        ('Контакты', {'fields': ('phone', 'email')}),

        ("Фото", {"fields": ("image",)}),
        ('Права доступа', {"fields": (
            "employee",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )}), (_("Important dates"), {"fields": ("last_login", "date_joined")})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('surname', 'name', 'patronymic','email', 'phone', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, CustomUserAdmin)