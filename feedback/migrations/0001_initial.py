# Generated by Django 3.2.12 on 2023-05-04 17:46

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0006_auto_20230504_2045'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackWithoutHomograph',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.PositiveBigIntegerField(verbose_name='ID пользователя')),
                ('text', models.TextField(verbose_name='Текст')),
                ('text_normalized', models.TextField(verbose_name='Нормализованный текст')),
                ('sent_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Когда был отправлен')),
            ],
            options={
                'verbose_name': 'Фидбек без омографа',
                'verbose_name_plural': 'Фидбеки без омографов',
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.PositiveBigIntegerField(verbose_name='ID пользователя')),
                ('text', models.TextField(verbose_name='Текст')),
                ('text_normalized', models.TextField(verbose_name='Нормализованный текст')),
                ('homograph_stressed', models.CharField(max_length=255, verbose_name='Омограф с проставленным ударением')),
                ('correct', models.BooleanField(default=True, verbose_name='Правильно?')),
                ('probability', models.JSONField(verbose_name='Распределение')),
                ('where_stress_should_be', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Где должно быть ударение')),
                ('sent_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Когда был отправлен')),
                ('homograph', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.homograph', verbose_name='Омограф')),
            ],
            options={
                'verbose_name': 'Фидбек',
                'verbose_name_plural': 'Фидбеки',
            },
        ),
    ]