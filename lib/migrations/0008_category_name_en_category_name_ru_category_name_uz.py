# Generated by Django 5.0.1 on 2024-03-27 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0007_alter_book_isbn_alter_book_reprint'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name_en',
            field=models.CharField(max_length=255, null=True, verbose_name='name'),
        ),
        migrations.AddField(
            model_name='category',
            name='name_ru',
            field=models.CharField(max_length=255, null=True, verbose_name='name'),
        ),
        migrations.AddField(
            model_name='category',
            name='name_uz',
            field=models.CharField(max_length=255, null=True, verbose_name='name'),
        ),
    ]
