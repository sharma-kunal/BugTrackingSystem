# Generated by Django 3.1.2 on 2020-10-07 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0002_auto_20201007_1337'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectuserrelation',
            old_name='project',
            new_name='project_id',
        ),
        migrations.RenameField(
            model_name='projectuserrelation',
            old_name='user',
            new_name='user_id',
        ),
        migrations.AlterField(
            model_name='projectuserrelation',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]