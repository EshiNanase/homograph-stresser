from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from gensim.models import KeyedVectors
from django.conf import settings
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
        verbose_name='Наиболее близкие по значению к семантич. классу'
    )
    quasi_synonyms = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name='Квазисинонимы'
    )

    class Meta:
        verbose_name = 'Квазисиноним'
        verbose_name_plural = 'Квазисинонимы'

    def __str__(self):
        return f'{self.homograph.homograph} - {",".join(self.synonyms)}'


@receiver(post_save, sender=QuasiSynonym)
def create_quasi_synonyms(sender, instance, created, **kwargs):

    try:
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
                for quasi_synonym, vector in quasi_synonyms:
                    quasi_synonym = morph.parse(quasi_synonym.split('_')[0])[0].normal_form.lower()
                    instance.quasi_synonyms[quasi_synonym] = vector
                instance.save()
    except KeyError:
        instance.delete()
