# Generated by Django 5.0.1 on 2024-04-16 12:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home_screen', '0003_meter_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrepaymentOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('confirmation_code', models.CharField(max_length=20)),
                ('selected_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home_screen.prepaymentoption')),
            ],
        ),
    ]
