# Generated by Django 3.2.7 on 2021-10-06 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_expenserecord_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenserecord',
            name='date',
            field=models.DateField(),
        ),
    ]
