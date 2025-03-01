# Generated by Django 5.0.1 on 2024-03-15 11:09

import lib.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0005_merge_20240228_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(max_length=20, validators=[lib.validators.validate_isbn], verbose_name='ISBN'),
        ),
    ]
