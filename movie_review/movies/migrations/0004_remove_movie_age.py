# Generated by Django 5.2.4 on 2025-07-14 06:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_cast'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='age',
        ),
    ]
