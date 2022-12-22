# Generated by Django 3.1.4 on 2021-01-10 14:55

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(default=uuid.uuid4, max_length=100)),
                ('event_name', models.CharField(max_length=120)),
                ('event_start', models.DateTimeField()),
                ('event_end', models.DateTimeField()),
                ('host', models.EmailField(max_length=100)),
                ('event_description', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pevent_id', models.CharField(max_length=100)),
                ('participant_email', models.EmailField(max_length=100)),
                ('participant_name', models.CharField(max_length=100)),
                ('participant_contactno', models.IntegerField()),
                ('group_registration', models.BooleanField()),
                ('no_of_members', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=250)),
            ],
        ),
    ]
