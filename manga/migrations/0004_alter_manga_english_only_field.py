# Generated by Django 4.2.4 on 2023-09-05 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manga", "0003_chapter_time_prod"),
    ]

    operations = [
        migrations.AlterField(
            model_name="manga",
            name="english_only_field",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
