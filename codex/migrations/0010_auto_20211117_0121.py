"""Generated by Django 3.2.9 on 2021-11-17 01:21."""

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    """Rename Library watch fields and add stat field."""

    dependencies = [
        ("codex", "0009_latestversion"),
    ]

    operations = [
        migrations.RenameField(
            model_name="library",
            old_name="enable_watch",
            new_name="events",
        ),
        migrations.RenameField(
            model_name="library",
            old_name="last_scan",
            new_name="last_poll",
        ),
        migrations.RenameField(
            model_name="library",
            old_name="enable_scan_cron",
            new_name="poll",
        ),
        migrations.RenameField(
            model_name="library",
            old_name="scan_in_progress",
            new_name="update_in_progress",
        ),
        migrations.RemoveField(
            model_name="library",
            name="scan_frequency",
        ),
        migrations.AddField(
            model_name="comic",
            name="stat",
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name="folder",
            name="stat",
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name="library",
            name="poll_every",
            field=models.DurationField(default=datetime.timedelta(seconds=3600)),
        ),
        migrations.AlterField(
            model_name="comic",
            name="size",
            field=models.PositiveIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name="folder",
            name="path",
            field=models.CharField(db_index=True, max_length=128),
        ),
        migrations.AlterField(
            model_name="folder",
            name="sort_name",
            field=models.CharField(db_index=True, max_length=32),
        ),
    ]
