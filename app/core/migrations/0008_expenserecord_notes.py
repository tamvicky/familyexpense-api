# Generated by Django 3.2.7 on 2021-10-05 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_expenserecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenserecord',
            name='notes',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
