# Generated by Django 5.1.4 on 2024-12-25 03:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('CustomManager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('store_id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True, verbose_name='用户唯一标识符')),
                ('store_name', models.CharField(max_length=255, verbose_name='store name')),
                ('address', models.CharField(max_length=255)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('district_code', models.IntegerField(unique=True, verbose_name='district code')),
                ('category', models.CharField(max_length=50)),
                ('average_rating', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('price_range', models.CharField(blank=True, max_length=50, null=True)),
                ('opening_hours', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'store information',
                'db_table': 't_store_manager',
            },
        ),
        migrations.CreateModel(
            name='StoreIdCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counter_name', models.CharField(max_length=50, unique=True)),
                ('current_value', models.PositiveIntegerField(default=100000)),
            ],
            options={
                'verbose_name': '商店iD管理',
                'verbose_name_plural': '商店管理ID',
                'db_table': 't_store_idcounter',
            },
        ),
        migrations.CreateModel(
            name='NearbyQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('radius', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='queries', to='CustomManager.userprofile')),
            ],
            options={
                'verbose_name': '店铺标签表',
                'db_table': 't_store_nearby_query',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CustomManager.userprofile')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='StoresManager.store')),
            ],
            options={
                'verbose_name': '店铺标签表',
                'db_table': 't_store_review',
            },
        ),
        migrations.CreateModel(
            name='StoreImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField()),
                ('image_type', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='StoresManager.store')),
            ],
            options={
                'verbose_name': '店铺标签表',
                'db_table': 't_store_image',
            },
        ),
        migrations.CreateModel(
            name='StorePromotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('promotion_type', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promotions', to='StoresManager.store')),
            ],
            options={
                'verbose_name': '店铺标签表',
                'db_table': 't_store_promotion',
            },
        ),
        migrations.CreateModel(
            name='StoreRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='StoresManager.store')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='CustomManager.userprofile')),
            ],
            options={
                'verbose_name': '店铺标签表',
                'db_table': 't_store_recommendation',
            },
        ),
        migrations.CreateModel(
            name='StoreTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='StoresManager.store')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='CustomManager.userprofile')),
            ],
            options={
                'verbose_name': '店铺标签表',
                'db_table': 't_store_tag',
            },
        ),
    ]
