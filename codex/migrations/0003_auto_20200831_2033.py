# Generated by Django 3.1 on 2020-08-31 20:33

import django.db.models.deletion

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("codex", "0002_auto_20200826_0622"),
    ]

    operations = [
        migrations.AlterField(
            model_name="credit",
            name="role",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="codex.creditrole",
            ),
        ),
    ]