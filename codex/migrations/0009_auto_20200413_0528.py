# Generated by Django 3.0.5 on 2020-04-13 05:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0008_auto_20200413_0501'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rootpath',
            old_name='scan_lock',
            new_name='scan_in_progress',
        ),
    ]