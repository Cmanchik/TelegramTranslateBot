import requests
import telebot
from telebot import types

import config
import teleMessage
from user import User

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)

keyboardMain = telebot.types.ReplyKeyboardMarkup(True, True)
keyboardMain.row("/translate", "/setting", "/help")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user = User()

    config.user_settings[str(message.from_user.id)] = user.serialisation()
    bot.send_message(message.chat.id, teleMessage.HELP, reply_markup=keyboardMain)


@bot.message_handler(commands=['setting'])
def setting(message):
    user = User(jsonStr=config.user_settings[str(message.from_user.id)])
    lang_format = user.first_lang + "-" + user.second_lang

    keyboard_choice = telebot.types.InlineKeyboardMarkup()
    first_lang_btn = types.InlineKeyboardButton(text="First lang",
                                                callback_data="choice-first-" + str(message.from_user.id) + "-" + str(
                                                    message.chat.id))
    second_lang_btn = types.InlineKeyboardButton(text="Second lang",
                                                 callback_data="choice-second-" + str(message.from_user.id) + "-" + str(
                                                     message.chat.id))

    keyboard_choice.add(first_lang_btn, second_lang_btn)
    bot.send_message(message.chat.id, teleMessage.CHOICE_NUM_LANG + lang_format, reply_markup=keyboard_choice)


@bot.message_handler(commands=['translate'])
def translate_control(message):
    user = User(jsonStr=config.user_settings[str(message.from_user.id)])

    user.is_translate = True
    user.choice_lang = 0

    config.user_settings[str(message.from_user.id)] = user.serialisation()

    lang_format = user.first_lang + "-" + user.second_lang
    bot.send_message(message.chat.id, teleMessage.TRANSLATE + lang_format)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    user = User(jsonStr=config.user_settings[str(message.from_user.id)])
    lang_format = user.first_lang + "-" + user.second_lang

    if user.is_translate:
        text = translate(message.text, lang_format)
        bot.send_message(message.chat.id, teleMessage.TRANSLATE_DONE + text)
    else:
        bot.send_message(message.chat.id, teleMessage.NOT_UNDERSTAND)


def translate(text, lang_dir):
    params = {
        'key': config.YANDEX_KEY,
        'text': text,
        'lang': lang_dir,
        'options': 1
    }

    response = requests.get(config.YANDEX_URL, params=params)
    return response.json()["text"][0]


def create_inline_langs(user_id, chat_id):
    markup = types.InlineKeyboardMarkup()

    for lang in list(config.LANGS.keys())[0:5]:
        button = types.InlineKeyboardButton(text=lang + "-" + config.LANGS.get(lang),
                                            callback_data="lang-" + lang + "-" + user_id + "-" + chat_id)
        markup.add(button)

    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    call = call.data.split('-')
    user = User(jsonStr=config.user_settings[call[2]])

    if call[0] == "lang":
        bot.send_message(int(call[3]), teleMessage.HELP, reply_markup=keyboardMain)
        user.choice_lang = 0

        if user.choice_lang == 1:
            user.first_lang = call[1]
        elif user.choice_lang == 2:
            user.second_lang = call[1]

    elif call[0] == 'choice':
        bot.send_message(int(call[3]), teleMessage.CHOICE_LANG, reply_markup=create_inline_langs(call[2], call[3]))

        if call[1] == 'first':
            user.choice_lang = 1
        elif call[2] == 'second':
            user.choice_lang = 2

    config.user_settings[call[2]] = user.serialisation()


bot.polling(none_stop=True)
