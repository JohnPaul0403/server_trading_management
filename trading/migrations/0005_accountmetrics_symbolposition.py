# Generated by Django 4.2.23 on 2025-06-27 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0004_remove_trade_profit_loss_remove_trade_trade_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_trades', models.IntegerField()),
                ('total_buy_qty', models.DecimalField(decimal_places=6, max_digits=20)),
                ('total_sell_qty', models.DecimalField(decimal_places=6, max_digits=20)),
                ('total_buy_cost', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total_sell_revenue', models.DecimalField(decimal_places=2, max_digits=20)),
                ('net_profit_loss', models.DecimalField(decimal_places=2, max_digits=20)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='trading.tradingaccount')),
            ],
        ),
        migrations.CreateModel(
            name='SymbolPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=20)),
                ('buy_qty', models.DecimalField(decimal_places=6, max_digits=20)),
                ('sell_qty', models.DecimalField(decimal_places=6, max_digits=20)),
                ('position', models.DecimalField(decimal_places=6, max_digits=20)),
                ('avg_buy_price', models.DecimalField(decimal_places=4, max_digits=20)),
                ('avg_sell_price', models.DecimalField(decimal_places=4, max_digits=20)),
                ('open_position', models.BooleanField()),
                ('unrealized_pl', models.DecimalField(decimal_places=2, max_digits=20)),
                ('current_price', models.DecimalField(blank=True, decimal_places=4, max_digits=20, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('account_metrics', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='symbol_positions', to='trading.accountmetrics')),
            ],
            options={
                'unique_together': {('account_metrics', 'symbol')},
            },
        ),
    ]
