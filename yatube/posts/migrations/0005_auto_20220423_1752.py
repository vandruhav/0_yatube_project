# Generated by Django 2.2.16 on 2022-04-23 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220422_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
