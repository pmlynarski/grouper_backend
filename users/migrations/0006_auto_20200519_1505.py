# Generated by Django 2.2.4 on 2020-05-19 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='media/'),
        ),
    ]
