# Generated by Django 4.2.4 on 2023-08-29 17:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manga", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("common", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Rating",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.IntegerField()),
                ("manga", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="manga.manga")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
