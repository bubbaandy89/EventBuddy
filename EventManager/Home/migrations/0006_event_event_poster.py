# Generated by Django 3.1.4 on 2021-01-20 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0005_auto_20210119_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_poster',
            field=models.URLField(default='', max_length=150),
        ),
    ]