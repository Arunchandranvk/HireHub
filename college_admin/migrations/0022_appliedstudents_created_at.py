# Generated by Django 5.1.5 on 2025-03-05 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('college_admin', '0021_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='appliedstudents',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
