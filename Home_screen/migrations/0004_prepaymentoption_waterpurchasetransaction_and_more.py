# Generated by Django 5.0.1 on 2024-04-24 07:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home_screen', '0003_meter_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaterPurchaseTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liters_purchased', models.IntegerField()),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
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