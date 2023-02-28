# Generated by Django 4.1.6 on 2023-02-27 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advanced_to_do', '0002_user_delete_images'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='images')),
            ],
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]