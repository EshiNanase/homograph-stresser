import textwrap
from core.models import Homograph, Feedback, FeedbackWithoutHomograph
from django.core.management.base import BaseCommand
import pymorphy2
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler, Updater
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
from django.conf import settings
from enum import Enum, auto, unique
from logger import ChatbotLogsHandler
from .stress_homograph import find_homograph, count_probability, make_stress

morph = pymorphy2.MorphAnalyzer(lang='ru')
logger = logging.getLogger(__file__)


@unique
class States(Enum):
    Text = auto()
    Accuracy = auto()


def start(update, context):
    text = textwrap.dedent(
        """
        Здравствуйте, я бот для снятия омографии.
        Просто отправьте мне какой-нибудь текст, в котором встречается омограф из списка в нормализованной форме, а я найду его и поставлю ударение в зависимости от контекста.
        
        Например: Я открыл замок ключом. => *зам'ок*. Замок стоял на горе => *з'амок*
        Список омографов открывается командой /homographs
        """
    )
    update.message.reply_text(text=text, parse_mode='Markdown')

    return States.Text


def send_possible_homographs(update, context):

    homographs = Homograph.objects.all().order_by('homograph')
    template = '*ВОЗМОЖНЫЕ ОМОГРАФЫ*'
    homographs_message = ', '.join(homograph.homograph for homograph in homographs)
    text = textwrap.dedent(
        f"""{template}\n\n"""
        f"""{homographs_message}"""
    )
    update.message.reply_text(text=text, parse_mode='Markdown')
    return States.Text


def handle_accuracy(update, context):

    message = update.message.text

    if 'Правильно' == message:

        Feedback.objects.create(
            user_id=update.message.chat_id,
            homograph=context.user_data['homograph'],
            text=context.user_data['text'],
            text_normalized=context.user_data['text_normalized'],
            homograph_stressed=context.user_data['homograph_stressed'],
            probability=context.user_data['probability']
        )

        message = 'Спасибо, фидбек отправлен! Отправляйте следующий текст!'
        update.message.reply_text(text=message, reply_markup=ReplyKeyboardRemove())

        return States.Text

    elif 'Неправильно' == message:

        message = 'Эх :(\n Напишите, пожалуйста, на каком слоге должно стоять ударение (цифрой)'
        update.message.reply_text(text=message)

        return States.Accuracy

    else:

        where_stress_should_be = int(message)
        Feedback.objects.create(
            user_id=update.message.chat_id,
            homograph=context.user_data['homograph'],
            text=context.user_data['text'],
            text_normalized=context.user_data['text_normalized'],
            homograph_stressed=context.user_data['homograph_stressed'],
            probability=context.user_data['probability'],
            correct=False,
            where_stress_should_be=where_stress_should_be
        )

        message = 'Спасибо, буду работать над ошибками! Отправляйте следующий текст!'
        update.message.reply_text(text=message, reply_markup=ReplyKeyboardRemove())

        return States.Text


def handle_sent_text(update, context):

    text_initial = update.message.text
    text_normalized, homograph = find_homograph(text_initial)

    if homograph:

        probability, homograph = count_probability(text_normalized, homograph)
        homograph_stressed = make_stress(string=homograph.homograph, n=max(probability, key=probability.get))

        context.user_data['homograph'] = homograph
        context.user_data['text'] = text_initial
        context.user_data['text_normalized'] = text_normalized
        context.user_data['homograph_stressed'] = homograph_stressed
        context.user_data['probability'] = probability

        message = textwrap.dedent(
            f"""
            Я думаю, что нужно поставить ударение так:
            
            *{homograph_stressed}*
            
            Пожалуйста, отметьте, правильно ли я поставил ударение или ошибся.
            """
        )
        
        keyboard = [
            ['Правильно', 'Неправильно']
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(text=message, reply_markup=reply_markup, parse_mode='Markdown')

        return States.Accuracy

    else:

        FeedbackWithoutHomograph.objects.create(user_id=update.message.chat_id, text=text_initial, text_normalized=text_normalized)
        update.message.reply_text(text='К сожалению, мне не удалось найти омограф! Отправьте новый текст, надеюсь, что с ним я справлюсь!')

        return States.Text


class Command(BaseCommand):
    help = 'Телеграм-бот, снимающий омографию'

    def handle(self, *args, **options):
        telegram_token = settings.TELEGRAM_TOKEN
        telegram_chat_id = settings.TELEGRAM_CHAT_ID

        logging.basicConfig(level=logging.WARNING)
        logger.addHandler(ChatbotLogsHandler(telegram_chat_id, telegram_token))

        updater = Updater(telegram_token)
        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                States.Text: [
                    CommandHandler('homographs', send_possible_homographs),
                    MessageHandler(Filters.text, handle_sent_text),
                ],
                States.Accuracy: [
                    CommandHandler('homographs', send_possible_homographs),
                    MessageHandler(Filters.text, handle_accuracy),
                ],
            },
            fallbacks=[],
            name='bot_conversation'
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
