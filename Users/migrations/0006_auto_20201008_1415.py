# Generated by Django 3.1.2 on 2020-10-08 14:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Users', '0005_auto_20201007_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projects',
            name='project_users',
            field=models.ManyToManyField(null=True, through='Users.ProjectUserRelation', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='projectuserrelation',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tickets',
            name='users',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Users',
        ),
    ]