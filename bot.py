import telebot
#from contextlib import suppress
import os
import time
import threading
import secret


status_send = False
count_got_files = 0
boss = '538231919'
bot = telebot.TeleBot(secret.token)
bot.send_message(boss, 'Бот перезапустился')


def send():
    global status_send
    try:
        files = os.listdir("temp")
        if files[0] == 'readme.txt':
            i = 1
        else:
            i = 0
        file_name = f'temp/{os.listdir("temp")[i]}'
        with open(file_name, 'rb') as photo:
            bot.send_photo(secret.channel, photo)
        with open(file_name, 'rb') as photo:
            bot.send_document(secret.channel, photo)
        os.remove(file_name)
        return True
    except Exception as e:
        bot.send_message(boss, f'send error\n\n{e}', disable_notification=True)
        return False


@bot.message_handler(commands=['send'])
def switch(message):
    global status_send, count_got_files
    id = str(message.chat.id)
    if id == boss:
        status_send = True
        count_got_files = 0
        bot.send_message(id, 'Отправка включена')


@bot.message_handler(commands=['count'])
def count(message):
    id = str(message.chat.id)
    all_files = len(os.listdir('temp')) - 1
    if id == boss:
        bot.send_message(id, f'Получено {count_got_files}, всего фоток {all_files}')


def post_timer():
    global status_send
    while True:
        if status_send:
            files = os.listdir('temp')
            if len(files) > 1:
                result = send()
                while not result:
                    time.sleep(60)
                    result = send()
                bot.send_message(boss, f'Фотка отправлена успешно, осталось {len(files) - 2} фоток', disable_notification=True)
                time.sleep(7200)
            else:
                status_send = False
                bot.send_message(boss, 'Фотки закончились')
        else:
            time.sleep(60)


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    global count_got_files
    id = str(message.chat.id)
    if id == boss:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_name = f'temp/{message.document.file_name}'
            with open(file_name, 'wb') as new_file:
                new_file.write(downloaded_file)
            count_got_files += 1
            bot.send_message(id, 'save')
        except Exception as e:
            bot.send_message(id, f'error, try again\n\n{e}')


if __name__ == '__main__':
    post_schedule = threading.Thread(target=post_timer)
    post_schedule.start()
    bot.polling(none_stop=True)
