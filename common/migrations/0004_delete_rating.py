# Generated by Django 4.2.4 on 2023-08-29 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0003_rating"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Rating",
        ),
    ]
