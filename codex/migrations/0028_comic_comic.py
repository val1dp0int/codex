# Generated by Django 3.1 on 2020-04-22 00:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('codex', '0027_auto_20200421_2314'),
    ]

    operations = [
        migrations.AddField(
            model_name='comic',
            name='comic',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='self', to='codex.comic'),
            preserve_default=False,
        ),
    ]