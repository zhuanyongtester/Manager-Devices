# Generated by Django 4.2.16 on 2024-10-09 02:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('work_number', models.CharField(max_length=150, primary_key=True, serialize=False, verbose_name='设备唯一标识符')),
                ('work_password', models.CharField(max_length=128)),
                ('work_name', models.CharField(default='', max_length=100, verbose_name='管理员的名字')),
                ('work_remark', models.CharField(default='', max_length=200, verbose_name='管理员描述')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=255, unique=True)),
                ('fresh_token', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('work_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserLogin.customuser')),
            ],
        ),
    ]