# Generated by Django 3.2.12 on 2022-04-12 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='random_avatar.jpg', upload_to='avatars'),
        ),
    ]