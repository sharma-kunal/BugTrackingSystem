# Generated by Django 3.1.2 on 2020-10-08 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0009_auto_20201008_1725'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tickets',
            name='submitter',
        ),
    ]
