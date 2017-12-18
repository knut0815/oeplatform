# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-14 11:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelview', '0032_auto_20160323_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='energyscenario',
            name='networks_electricity_gas_electricity',
            field=models.BooleanField(default=False, verbose_name='electricity'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='energyscenario',
            name='networks_electricity_gas_gas',
            field=models.BooleanField(default=False, verbose_name='gas'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='basicfactsheet',
            name='logo',
            field=models.ImageField(null=True, upload_to='logos', verbose_name='Logo'),
        ),
        migrations.AlterField(
            model_name='energymodel',
            name='transfer_electricity_transition',
            field=models.BooleanField(default=False, verbose_name='transmission'),
        ),
        migrations.AlterField(
            model_name='energymodel',
            name='transfer_gas_transition',
            field=models.BooleanField(default=False, verbose_name='transmission'),
        ),
        migrations.AlterField(
            model_name='energymodel',
            name='transfer_heat_transition',
            field=models.BooleanField(default=False, verbose_name='transmission'),
        ),
    ]