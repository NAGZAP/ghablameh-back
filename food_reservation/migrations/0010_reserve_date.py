# Generated by Django 5.0.2 on 2024-06-04 11:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_reservation', '0009_alter_mealfood_meal'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserve',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
