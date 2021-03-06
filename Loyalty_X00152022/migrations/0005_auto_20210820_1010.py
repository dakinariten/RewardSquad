# Generated by Django 3.2.6 on 2021-08-20 09:10

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Loyalty_X00152022', '0004_auto_20210816_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeuser',
            name='rp_acc_link',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='historicaloffers',
            name='date_end',
            field=models.DateField(default=datetime.datetime(2021, 8, 27, 9, 10, 27, 402097, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='historicaloffers',
            name='date_start',
            field=models.DateField(default=datetime.datetime(2021, 8, 20, 9, 10, 27, 402097, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='historicalorder',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 20, 9, 10, 27, 399099, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='offers',
            name='date_end',
            field=models.DateField(default=datetime.datetime(2021, 8, 27, 9, 10, 27, 402097, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='offers',
            name='date_start',
            field=models.DateField(default=datetime.datetime(2021, 8, 20, 9, 10, 27, 402097, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 20, 9, 10, 27, 399099, tzinfo=utc)),
        ),
    ]
