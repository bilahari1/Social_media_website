# Generated by Django 3.0.2 on 2023-03-30 10:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0018_jobposting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobposting',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.Company'),
        ),
    ]
