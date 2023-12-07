from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UsernameField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.workers.models import User

