import textwrap

from django.core.management.base import BaseCommand
from string import punctuation
from core.models import Homograph
import pymorphy2

morph = pymorphy2.MorphAnalyzer(lang='ru')


def start(update, context):
    text = textwrap.dedent(
        """
        Здравствуйте, я бот для снятия омографии.
        Просто отправьте мне какой-нибудь текст, 
        """
    )


def rip_punctuation(sentence):
    for symbol in punctuation:
        sentence = sentence.replace(symbol, '')
    sentence = " ".join(sentence.split())
    return sentence


def find_homograph(text_initial):

    sentence = rip_punctuation(text_initial).split(' ')
    homographs = Homograph.objects.prefetch_related('quasis').all()

    text_normalized = []
    homographs_found = []
    for word in sentence:

        word = morph.parse(word)[0].normal_form.lower()
        text_normalized.append(word)
        homograph = homographs.filter(homograph=word)

        if homograph:
            homographs_found.append(homograph.first())

    if not homographs_found:
        return text_normalized, False

    return text_normalized, homographs_found[0]


def make_stress(string, n):
    vowels = ['у', 'а', 'е', 'ы', 'о', 'э', 'я', "и", "ю"]

    vowel_placement = [letter for letter in range(len(string)) if string[letter] in vowels][n]
    string = string[:vowel_placement] + "'" + string[vowel_placement:]
    return string


def count_probability(sentence_normalized, homograph):
    main_quasis = homograph.quasis.all()
    probability = {quasi.stress: 0 for quasi in main_quasis}
    for word in sentence_normalized:
        for main_quasi in main_quasis:
            if word in main_quasi.quasi_synonyms:
                probability[main_quasi.stress] += 1
    return probability, homograph


class Command(BaseCommand):
    help = 'Снятие омографии'

    def handle(self, *args, **options):
        text_initial = input('Введите текст:\n')
        text_normalized, homograph = find_homograph(text_initial)

        if not homograph:
            raise RuntimeError('Омограф не найден!')

        probability, homograph = count_probability(text_normalized, homograph)

        print(make_stress(string=homograph.homograph, n=max(probability, key=probability.get)))
