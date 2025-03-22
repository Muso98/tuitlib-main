from enum import Enum
from django.utils import timezone
from datetime import timedelta
from django.db import models
from lib.models import Book
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import re
from .managers import UserManager
from lib.models import Book
from django.utils.translation import gettext_lazy as _
from .enums import UserType


def phone_number_validator(value):
    pattern = re.compile(r'^\+998\d{9}$')
    if re.match(pattern, value):
        return True
    return False


class ResearchArea(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email"), help_text="Required. Inform a valid email", unique=True)
    first_name = models.CharField(_("first_name"), max_length=50, blank=True, null=True)
    last_name = models.CharField(_("last_name"), max_length=50, blank=True, null=True)
    phone_number = models.CharField(_("phone_number"), max_length=15, blank=True, null=True,
                                    validators=[phone_number_validator])
    role = models.CharField(max_length=100, choices=UserType.choices(), blank=True, null=True)
    research_area = models.ManyToManyField(ResearchArea, blank=True)
    interests = models.CharField(max_length=1024, blank=True, null=True)
    birth_date = models.DateField(_("birth date"), blank=True, null=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Downloads(models.Model):
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.user.email} | {self.book.name}'


class ResponseChoices(Enum):
    PENDING = _('pending')
    ACCEPTED = _('accepted')
    REJECTED = _('rejected')

    @classmethod
    def choices(cls):
        return ((i.name, i.value) for i in cls)


RESPONSE_CHOICES = (
    ('pending', _('pending')),
    ('accepted', _('accepted')),
    ('rejected', _('rejected'))
)


class Requests(models.Model):
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status_request = models.CharField(max_length=20, choices=RESPONSE_CHOICES, default=RESPONSE_CHOICES[0][0])

    def __str__(self):
        return f'{self.user.email} | {self.book.name}'

    class Meta:
        verbose_name = _("Request")
        verbose_name_plural = _("Requests")


class EmailOTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    @property
    def code_end_time(self):
        return self.created_at + timedelta(minutes=2)

    @property
    def is_active(self) -> bool:
        return timezone.now() > self.code_end_time


class FaceID(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="face_id")
    aws_face_id = models.CharField(max_length=255, blank=True, null=True)  # AWS Rekognition ID
    image = models.ImageField(upload_to="face_images/")  # Foydalanuvchi yuz tasviri
    created_at = models.DateTimeField(auto_now_add=True)  # Yaratilgan sana

    def __str__(self):
        return f"{self.user.email} Face ID"



class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    query = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} | {self.query}'
