"""Generated by Django 4.0.1 on 2022-01-16 05:31."""

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):
    """Haystack search engine."""

    dependencies = [
        ("codex", "0009_alter_comic_parent_folder"),
    ]

    operations = [
        migrations.CreateModel(
            # Fake model. Not managed.
            name="QueueJob",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "db_tablespace": "temp",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="SearchQuery",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(db_index=True, max_length=256, unique=True)),
                ("used_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name="latestversion",
            options={"get_latest_by": "updated_at"},
        ),
        migrations.CreateModel(
            name="SearchResult",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.PositiveSmallIntegerField()),
                (
                    "comic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="codex.comic"
                    ),
                ),
                (
                    "query",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="codex.searchquery",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="searchresult",
            index=models.Index(
                fields=["comic", "query"], name="codex_searc_comic_i_dd09ab_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="searchresult",
            unique_together={("query", "comic")},
        ),
    ]
