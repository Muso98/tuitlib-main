# Generated by Django 5.0.1 on 2024-02-26 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='reprint',
            field=models.CharField(blank=True, help_text='Qayta nashr yili. Kiritish: Qayta nashr: {yil}', max_length=255, null=True, verbose_name='reprint'),
        ),
    ]
