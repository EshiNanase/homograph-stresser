from django.db import models
from django.utils import timezone


class FeedbackWithoutHomograph(models.Model):

    user_id = models.PositiveBigIntegerField(
        verbose_name='ID пользователя'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    text_normalized = models.TextField(
        verbose_name='Нормализованный текст'
    )
    sent_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Когда был отправлен'
    )

    class Meta:
        verbose_name = 'Фидбек без омографа'
        verbose_name_plural = 'Фидбеки без омографов'

    def __str__(self):
        return f'{self.sent_at.strftime("%d.%m %H:%M")}'


class Feedback(models.Model):

    user_id = models.PositiveBigIntegerField(
        verbose_name='ID пользователя'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    text_normalized = models.TextField(
        verbose_name='Нормализованный текст'
    )
    homograph = models.ForeignKey(
        to='core.Homograph',
        on_delete=models.CASCADE,
        verbose_name='Омограф'
    )
    homograph_stressed = models.CharField(
        max_length=255,
        verbose_name='Омограф с проставленным ударением'
    )
    correct = models.BooleanField(
        default=True,
        verbose_name='Правильно?'
    )
    probability = models.JSONField(
        verbose_name='Распределение'
    )

    # IF NOT CORRECT

    where_stress_should_be = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Где должно быть ударение'
    )
    sent_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Когда был отправлен'
    )

    class Meta:
        verbose_name = 'Фидбек'
        verbose_name_plural = 'Фидбеки'

    def __str__(self):
        return f'{self.homograph.homograph} - {"Правильно" if self.correct else "Неправильно"} - {self.sent_at.strftime("%d.%m %H:%M")}'
