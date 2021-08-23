# Generated by Django 3.2.6 on 2021-08-16 13:12

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Loyalty_X00152022', '0002_auto_20210816_0024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaloffers',
            name='date_end',
            field=models.DateField(default=datetime.datetime(2021, 8, 23, 13, 12, 5, 552315, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='historicaloffers',
            name='date_start',
            field=models.DateField(default=datetime.datetime(2021, 8, 16, 13, 12, 5, 552315, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='historicalorder',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 16, 13, 12, 5, 550314, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='historicaluserdetails',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='offers',
            name='date_end',
            field=models.DateField(default=datetime.datetime(2021, 8, 23, 13, 12, 5, 552315, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='offers',
            name='date_start',
            field=models.DateField(default=datetime.datetime(2021, 8, 16, 13, 12, 5, 552315, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 16, 13, 12, 5, 550314, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='userdetails',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
