# Generated by Django 4.2.4 on 2023-08-21 10:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0009_alter_articleposts_options_articleposts_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='articleposts',
            name='article_tag',
            field=models.CharField(blank=True, default='', max_length=10, null=True, validators=[django.core.validators.MinLengthValidator(5)]),
        ),
    ]
