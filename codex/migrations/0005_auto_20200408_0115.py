# Generated by Django 3.0.5 on 2020-04-08 01:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0004_auto_20200407_2151'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='folder',
            unique_together={('root_path', 'path')},
        ),
    ]