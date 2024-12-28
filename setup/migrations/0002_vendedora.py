# Generated by Django 5.1.4 on 2024-12-28 17:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendedora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('foto', models.ImageField(blank=True, null=True, upload_to='vendedoras/')),
                ('logradouro', models.CharField(max_length=200)),
                ('bairro', models.CharField(max_length=100)),
                ('cidade', models.CharField(max_length=100)),
                ('uf', models.CharField(max_length=2)),
                ('telefone1', models.CharField(max_length=20)),
                ('telefone2', models.CharField(blank=True, max_length=20, null=True)),
                ('observacoes', models.TextField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendedora', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
