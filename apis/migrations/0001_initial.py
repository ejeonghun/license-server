# Generated by Django 5.1.4 on 2025-01-09 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='License',
            fields=[
                ('license_key', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('hash_key', models.CharField(max_length=100)),
                ('is_activation', models.BooleanField(default=False)),
                ('activation_date', models.DateTimeField(blank=True, null=True)),
                ('user_name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('company', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
