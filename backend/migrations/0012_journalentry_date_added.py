# Generated by Django 5.1.1 on 2024-10-17 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0011_journalentry_calculated_risk_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalentry',
            name='date_added',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
