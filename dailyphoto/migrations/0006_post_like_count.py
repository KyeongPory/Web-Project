# Generated by Django 4.0.2 on 2022-02-10 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dailyphoto', '0005_alter_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='like_count',
            field=models.IntegerField(null=True),
        ),
    ]