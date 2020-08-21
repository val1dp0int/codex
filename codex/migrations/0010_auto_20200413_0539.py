# Generated by Django 3.0.5 on 2020-04-13 05:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0009_auto_20200413_0528'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adminflag',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='character',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='comic',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='credit',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='creditperson',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='creditrole',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='folder',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='genre',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='imprint',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='location',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='rootpath',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='series',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='seriesgroup',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='storyarc',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='team',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='volume',
            name='deleted_at',
        ),
    ]