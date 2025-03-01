from django.contrib import admin
from .models import *
from django.db import models
from django.forms import ModelForm, CheckboxSelectMultiple


class BookAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple}
    }
    exclude = ['download_count', ]


admin.site.register(Book, BookAdmin)
admin.site.register(University)
admin.site.register(ResourceType)
admin.site.register(Category)
admin.site.register(Library)
admin.site.register(ResourceArea)
