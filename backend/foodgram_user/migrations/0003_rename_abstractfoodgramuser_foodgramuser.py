# Generated by Django 5.1.7 on 2025-05-31 13:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_delete_subscription'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('foodgram_user', '0002_subscription'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AbstractFoodgramUser',
            new_name='FoodgramUser',
        ),
    ]
