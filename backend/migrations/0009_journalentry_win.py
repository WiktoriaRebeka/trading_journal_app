# Generated by Django 5.1.1 on 2024-10-10 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_remove_journalentry_win'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalentry',
            name='win',
            field=models.CharField(blank=True, choices=[('YES', 'YES'), ('NO', 'NO')], max_length=3, null=True),
        ),
    ]
