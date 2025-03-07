from django.contrib import admin
from .models import *
from django.db import models
from django.forms import ModelForm, CheckboxSelectMultiple


class BookAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple}
    }
    exclude = ['download_count']
    list_display = ('name', 'author', 'published_year', 'language', 'category')  # ✅ Ustunlar
    search_fields = ('name', 'author', 'key_words')  # ✅ Qidirish
    list_filter = ('language', 'category')  # ✅ Filtr qo‘shish

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class UniversityAdmin(admin.ModelAdmin):
    search_fields = ('name', 'country')

class LibraryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address')


admin.site.register(Book, BookAdmin)
admin.site.register(ResourceType)
admin.site.register(Category, CategoryAdmin)
admin.site.register(University, UniversityAdmin)
admin.site.register(Library, LibraryAdmin)
admin.site.register(ResourceArea)
admin.site.register(Notification)
admin.site.register(SearchQuery)
