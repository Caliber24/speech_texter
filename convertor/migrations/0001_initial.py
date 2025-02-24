# Generated by Django 5.1.6 on 2025-02-23 18:46

import convertor.validatiors
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VTT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio', models.FileField(help_text='Enter the path to the audio file.', max_length=255, upload_to='audio/%Y/%m/%d', validators=[convertor.validatiors.validate_audio_file])),
                ('transcript', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
