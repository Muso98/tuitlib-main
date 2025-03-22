from django.db import models
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .validators import validate_isbn
from django.contrib.auth.models import User
from django.conf import settings  # settings.AUTH_USER_MODEL ni olish uchun
from django.contrib.postgres.search import TrigramSimilarity
from django.utils.timezone import now
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(_("name"), max_length=255)

    def __str__(self):
        return f"{str(self.id)} - {self.name} "

    class Meta:
        ordering = ['-id']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class University(models.Model):
    name = models.CharField(_("name"), max_length=100)
    about = models.TextField(_("about"), blank=True, null=True)
    country = models.CharField(_("country"), max_length=100, blank=True, null=True)
    area = models.CharField(_("area"), max_length=100, blank=True, null=True)
    phone_number = models.CharField(_("phone_number"), max_length=13, blank=True, null=True)
    website = models.URLField(_("website"), blank=True, null=True)
    email = models.EmailField(_("email"), blank=True, null=True)
    address = models.CharField(_("address"), max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("University")
        verbose_name_plural = _("Universities")


class ResourceType(models.Model):
    name = models.CharField(_("name"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Resource Type")
        verbose_name_plural = _("Resource Types")


LANGUAGE_CHOICES = (
    ('UzbekLatin', _('Uzbek-Latin')),
    ('UzbekKiril', _('Uzbek-Kiril')),
    ('Russian', _('Russian')),
    ('English', _('English'))
)

PERMISSIONS_CHOICES = (
    ('public', _('public')),
    ('private', _('private'))
)


class ResourceArea(models.Model):
    name = models.CharField(_("name"), max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Resource Area")
        verbose_name_plural = _("Resource Areas")


class Library(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    image = models.ImageField(upload_to='images/%Y/%m/%d')
    location = models.URLField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone_number = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Library")
        verbose_name_plural = _("Libraries")


class Book(models.Model):
    name = models.CharField(_("name"), max_length=255)
    isbn = models.CharField(_("ISBN"), max_length=20, validators=[validate_isbn], unique=True, blank=True, null=True)
    reprint = models.BooleanField(_("reprint"), default=False,
                                  help_text=_("Agar kitob qayta nashr qilingan bo'lsa qayta nashr yilini kiriting"))
    published_year = models.CharField(_("published_year"), max_length=20)
    pages = models.IntegerField(_("Pages Count"), default=0)
    resource_area = models.ForeignKey(ResourceArea, blank=True, null=True, help_text=_("Resource Area"),
                                      on_delete=models.SET_NULL)
    library = models.ManyToManyField(Library, blank=True, help_text=_("Library"))
    key_words = models.TextField(_("key_words"))
    about = models.TextField(_("about"))
    author = models.TextField(_("author"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True)
    resource_type = models.ForeignKey(ResourceType, on_delete=models.SET_NULL, null=True)
    publisher = models.CharField(_("publisher"), max_length=255, blank=True, null=True)
    language = models.CharField(_("language"), max_length=25, choices=LANGUAGE_CHOICES,
                                default=LANGUAGE_CHOICES[0][0])
    file = models.FileField(_("file"), upload_to='files/%Y/%m/%d/', help_text="Resurs fayli")
    image = models.ImageField(_("image"), upload_to='images/%Y/%m/%d/', help_text="Resurs rasmi")
    permission = models.CharField(_("permission"), max_length=10, choices=PERMISSIONS_CHOICES)
    download_count = models.IntegerField(_("download_count"), default=0)

    def __str__(self):
        return self.name

    def get_file_path(self):
        return self.file.url


    def similar_books(self):
        return Book.objects.annotate(
            similarity=TrigramSimilarity('key_words', self.key_words)
        ).filter(similarity__gt=0.3).exclude(id=self.id).order_by('-similarity')[:8]

    def get_absolute_url(self):
        return reverse("book", args=[str(self.id)])

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")


class STTModel(models.Model):
    access = models.TextField(_("access_token"))
    refresh = models.TextField(_("refresh_token"))

    def __str__(self):
        return self.id

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    book = models.ForeignKey("lib.Book", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # ✅ O‘qilganligini belgilash

    def __str__(self):
        return f"Notification for {self.user} - {'Read' if self.is_read else 'Unread'}"




class SearchQuery(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Search Query: {self.title} by {self.user}"

    @staticmethod
    def cleanup_old_queries(days=30):
        """Eski qidiruvlarni avtomatik tozalash"""
        old_date = now() - timedelta(days=days)
        SearchQuery.objects.filter(created_at__lt=old_date).delete()
