# Generated by Django 5.2.2 on 2025-06-13 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssh_panel', '0005_commandshortcut'),
    ]

    operations = [
        migrations.AddField(
            model_name='container',
            name='output',
            field=models.TextField(blank=True, default=''),
        ),
    ]
