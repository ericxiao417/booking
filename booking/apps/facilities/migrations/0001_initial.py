# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('location', models.CharField(max_length=200, verbose_name='location')),
                ('capacity', models.PositiveIntegerField(verbose_name='capacity')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('image', models.ImageField(blank=True, null=True, upload_to='facilities/', verbose_name='image')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('opening_time', models.TimeField(blank=True, null=True, verbose_name='opening time')),
                ('closing_time', models.TimeField(blank=True, null=True, verbose_name='closing time')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'facility',
                'verbose_name_plural': 'facilities',
                'ordering': ['name'],
            },
        ),
        migrations.AddIndex(
            model_name='facility',
            index=models.Index(fields=['name'], name='facilities__name_07d060_idx'),
        ),
        migrations.AddIndex(
            model_name='facility',
            index=models.Index(fields=['is_active'], name='facilities__is_acti_edaa96_idx'),
        ),
        migrations.AddIndex(
            model_name='facility',
            index=models.Index(fields=['location'], name='facilities__locatio_b27b9d_idx'),
        ),
    ]
