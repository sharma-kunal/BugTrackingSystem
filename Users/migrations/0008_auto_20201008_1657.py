# Generated by Django 3.1.2 on 2020-10-08 16:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Users', '0007_auto_20201008_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectuserrelation',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterUniqueTogether(
            name='projectuserrelation',
            unique_together={('user_id', 'project_id')},
        ),
    ]