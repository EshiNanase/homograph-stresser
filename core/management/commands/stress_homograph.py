from django.core.management.base import BaseCommand
from string import punctuation
from core.models import Homograph
import pymorphy2

morph = pymorphy2.MorphAnalyzer(lang='ru')


def rip_punctuation(sentence):
    symbols = punctuation + '»' + '«'
    for symbol in symbols:
        sentence = sentence.replace(symbol, '')
    sentence = " ".join(sentence.split())
    return sentence


def find_homograph(text_initial):

    sentence = rip_punctuation(text_initial).split(' ')
    homographs = Homograph.objects.prefetch_related('quasis').all()
    
    text_normalized = []
    homographs_found = []
    for word in sentence:

        word_parsed = morph.parse(word)[0]

        if word_parsed.tag.POS == 'PREP':
            continue

        word = word_parsed.normal_form.lower()
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


def count_weights(sentence_normalized, homograph):
    main_quasis = homograph.quasis.all()
    weights = {quasi.stress: quasi.initial_weight for quasi in main_quasis}
    for word in sentence_normalized:
        for main_quasi in main_quasis:
            if word in main_quasi.quasi_synonyms:
                weights[main_quasi.stress] += main_quasi.quasi_synonyms[word]
    return weights, homograph


class Command(BaseCommand):
    help = 'Снятие омографии'

    def handle(self, *args, **options):
        text_initial = input('Введите текст:\n')
        text_normalized, homograph = find_homograph(text_initial)

        if not homograph:
            raise RuntimeError('Омограф не найден!')

        weights, homograph = count_weights(text_normalized, homograph)

        print(make_stress(string=homograph.homograph, n=max(weights, key=weights.get)))
