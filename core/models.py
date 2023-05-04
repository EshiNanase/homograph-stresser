from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from gensim.models import KeyedVectors
from django.conf import settings
from django.utils import timezone
import pymorphy2


class Homograph(models.Model):

    homograph = models.CharField(
        max_length=255,
        verbose_name='Омограф'
    )

    class Meta:
        verbose_name = 'Омограф'
        verbose_name_plural = 'Омографы'

    def __str__(self):
        return self.homograph


class QuasiSynonym(models.Model):

    homograph = models.ForeignKey(
        to=Homograph,
        on_delete=models.CASCADE,
        related_name='quasis',
        verbose_name='Омограф'
    )
    stress = models.PositiveSmallIntegerField(
        verbose_name='На какой слог ударение (с нуля)'
    )
    synonyms = models.JSONField(
        default=list,
        verbose_name='Наиболее близкие по значению к семантич. классу'
    )
    quasi_synonyms = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name='Квазисинонимы'
    )

    class Meta:
        verbose_name = 'Квазисиноним'
        verbose_name_plural = 'Квазисинонимы'

    def __str__(self):
        return f'{self.homograph.homograph} - {",".join(self.synonyms)}'


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


class Feedback(FeedbackWithoutHomograph):

    homograph = models.ForeignKey(
        to=Homograph,
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

    class Meta:
        verbose_name = 'Фидбек'
        verbose_name_plural = 'Фидбеки'

    def __str__(self):
        return f'{self.homograph.homograph} - {"Правильно" if self.correct else "Неправильно"} - {self.sent_at.strftime("%d.%m %H:%M")}'


@receiver(post_save, sender=QuasiSynonym)
def create_quasi_synonyms(sender, instance, created, **kwargs):

    if created:
        model = KeyedVectors.load_word2vec_format(settings.MODEL_PATH, binary=True)
        morph = pymorphy2.MorphAnalyzer(lang='ru')

        if len(instance.synonyms) == 3:
            quantity = 100
        elif len(instance.synonyms) == 2:
            quantity = 150
        else:
            quantity = 300

        for synonym in instance.synonyms:
            tag = morph.parse(synonym)[0].tag.POS

            if tag == 'ADJF':
                tag = tag.replace('F', '')
            elif tag == 'INFN':
                tag = tag.replace('INFN', 'VERB')

            quasi_synonyms = model.most_similar(positive=synonym + '_' + tag, topn=quantity)
            for quasi_synonym in quasi_synonyms:
                quasi_synonym = morph.parse(quasi_synonym[0].split('_')[0])[0].normal_form.lower()
                instance.quasi_synonyms.append(quasi_synonym)
            instance.save()
