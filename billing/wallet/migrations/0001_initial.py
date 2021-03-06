# Generated by Django 3.2 on 2021-04-18 13:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'wallets',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_anonymous', models.BooleanField(default=False)),
                ('comment', models.CharField(blank=True, default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='received_payments', to='wallet.wallet')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sent_payments', to='wallet.wallet')),
            ],
            options={
                'db_table': 'transactions',
                'ordering': ('-created_at',),
            },
        ),
    ]
