# Generated by Django 5.1.4 on 2024-12-18 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CustomManager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='user_id',
            field=models.CharField(max_length=255, primary_key=True, serialize=False, unique=True, verbose_name='用户唯一标识符'),
        ),
    ]