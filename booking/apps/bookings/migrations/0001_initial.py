# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('facilities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('start_time', models.DateTimeField(verbose_name='start time')),
                ('end_time', models.DateTimeField(verbose_name='end time')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending', max_length=20, verbose_name='status')),
                ('number_of_people', models.PositiveIntegerField(default=1, verbose_name='number of people')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='facilities.facility', verbose_name='facility')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'booking',
                'verbose_name_plural': 'bookings',
                'ordering': ['-start_time'],
            },
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['user'], name='bookings_bo_user_id_6a6c3a_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['facility'], name='bookings_bo_facilit_d42c9a_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['status'], name='bookings_bo_status_4e2153_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['start_time', 'end_time'], name='bookings_bo_start_t_4d5d70_idx'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(check=models.Q(('end_time__gt', models.F('start_time'))), name='end_time_after_start_time'),
        ),
    ]
