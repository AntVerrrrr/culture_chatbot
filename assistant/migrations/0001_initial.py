# Generated by Django 4.2.16 on 2024-09-30 09:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CityCountyTown',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('province', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='assistant.province')),
            ],
        ),
        migrations.CreateModel(
            name='Assistant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assistant_id', models.CharField(default='default_assistant_id', max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='assistant_photos/')),
                ('description', models.TextField(default='No description available')),
                ('country', models.CharField(default='대한민국', max_length=100)),
                ('document_id', models.CharField(blank=True, max_length=255, null=True)),
                ('city_county_town', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistant.citycountytown')),
                ('province', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='assistant.province')),


            ],
        ),
    ]
