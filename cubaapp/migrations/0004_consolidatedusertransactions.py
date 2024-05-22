# Generated by Django 4.1.4 on 2024-05-22 17:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cubaapp', '0003_activitylog_appopens_brands_bucketlists_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsolidatedUserTransactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_sales', models.DecimalField(decimal_places=2, max_digits=20)),
                ('average_sales', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total_transactions', models.IntegerField()),
                ('total_items', models.IntegerField()),
                ('total_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('last_transaction_date', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cubaapp.users')),
            ],
            options={
                'db_table': 'consolidated_user_transactions',
            },
        ),
    ]
