# Generated by Django 5.1.4 on 2024-12-28 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0006_produto_quantidade'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('endereco', models.CharField(max_length=200)),
            ],
        ),
    ]
