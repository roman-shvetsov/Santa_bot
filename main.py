import telebot
import random
import sqlite3

bot = telebot.TeleBot('5681456371:AAEiQelZJqNzEwUhr89cXjujhVFdci1MhmY')

dreams = {}

conn = sqlite3.connect('data.db', check_same_thread=False)
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, dreams TEXT)')


# считывает команду start
@bot.message_handler(commands=['start'])
def start(message):
    who_gets = []
    who_gives = []
    entities = (message.chat.id, message.from_user.username)
    block = 0
    tabele = cur.execute('''INSERT OR IGNORE INTO users (user_id, username) VALUES(?, ?)''', entities)
    #cur.execute(f'UPDATE users SET block = ("{1}") WHERE user_id = ("{message.chat.id}")')

    mess = f"Привет, {message.from_user.first_name}❄\n\n" \
           f"Теперь ты в игре *\"Тайный Дед\"*\. \nЭто забавная игра, когда каждый покупает подарки для другого человека, который не знает, кто купил его подарок\." \
           f"\n\nБюджет в этом году составляет *500 рублей*\.\n\n" \
           f"Не могу дождаться, когда увидимся все вместе и будем дарить подарки🎁 \n\n\n" \
           f"В ответ на данное сообщение напиши, пожалуйста, одним сообщением о своих интересах и какой подарок ты хочешь получить в ответ, чтобы упростить работу твоему *\"Тайному Деду\"*🎄"

    if message.from_user.username not in who_gives:
        who_gives.append(message.from_user.username)
        who_gets.append(message.from_user.username)
        print("Список участников: ", who_gives)

        bot.send_message(message.chat.id, mess, parse_mode='MarkdownV2')
    else:
        bot.send_message(message.chat.id, 'Ты уже есть в списке.')

    conn.commit()

@bot.message_handler(commands=['go'])
def go(message):
    bot.send_message(message.chat.id, 'Йо-хо-хо, Начали!')
    username = cur.execute(f'SELECT username FROM users')
    who_gives = username.fetchall()
    who_gets = list.copy(who_gives)

    while len(who_gives) != 0:
        partner_gives = random.choice(who_gives)  # Выбираем рандомно из списка дарящих
        partner_gets = random.choice(who_gets)  # Выбираем рандомно из списка получающих

        if partner_gets != partner_gives:
            print(partner_gives, " дарит подарок ", partner_gets)
            ptgets = cur.execute(f'SELECT username, dreams FROM users WHERE (username) = ("{partner_gets[0]}")')  #запрос для получения имени, кому дарят и мечты
            result = ptgets.fetchall()
            ptgives = cur.execute(f'SELECT user_id FROM users WHERE (username) = ("{partner_gives[0]}")')  #Запрос для получения айди, кто дарит
            result_id = ptgives.fetchall()
            bot.send_message(result_id[0][0], f'Человек, которому ты будешь дарить подарок это @{result[0][0]}☃\n\nЕго пожелания: {result[0][1]}\n\n\n'
                                              f'Надеюсь у всех получится поднять друг другу праздничное настроение и сблизиться с людьми, которые сражаются каждый день бок о бок с вами против недовольных партнёров❤️‍🔥') #отправка конечного сообщения
            who_gives.remove(partner_gives)
            who_gets.remove(partner_gets)

    conn.commit()


# Отвечает на присланный текст
@bot.message_handler(content_types=['text'])
def get_user_text(message):
    cur.execute(f'UPDATE users SET dreams = ("{message.text}") WHERE user_id = ("{message.chat.id}")')
    if message.from_user.username not in dreams:
        people = message.from_user.username
        dreams[people] = message.text
        bot.send_message(message.chat.id, 'Спасибо, я получил твоё письмо💌\nЕсли передумаешь, напиши другое🎁 ')
    elif message.from_user.username in dreams:
        people = message.from_user.username
        dreams[people] = message.text
        bot.send_message(message.chat.id, 'Вы изменили своё желание.')
    print(dreams)
    conn.commit()

bot.polling(none_stop=True)
