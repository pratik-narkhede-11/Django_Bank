# Generated by Django 5.1.3 on 2024-12-09 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mybank', '0002_alter_account_id_alter_customer_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='final_balace',
            new_name='final_balance',
        ),
        migrations.AlterField(
            model_name='account',
            name='type',
            field=models.CharField(max_length=10),
        ),
    ]
