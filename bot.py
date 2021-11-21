import telebot
#from contextlib import suppress
import os
import time
import threading
import secret


status_send = False
count_got_files = 0
bot = telebot.TeleBot(secret.token)
bot.send_message(538231919, 'Бот перезапустился')


def send():
    global status_send
    file_name = f'temp/{os.listdir("temp")[0]}'
    try:
        with open(file_name, 'rb') as photo:
            bot.send_photo(secret.channel, photo)
        with open(file_name, 'rb') as photo:
            bot.send_document(secret.channel, photo)
        os.remove(file_name)
        return True
    except Exception as e:
        bot.send_message(538231919, f'send error\n\n{e}', disable_notification=True)
        return False


@bot.message_handler(commands=['send'])
def switch(message):
    global status_send, count_got_files
    id = str(message.chat.id)
    if id == '538231919':
        status_send = True
        count_got_files = 0
        bot.send_message(id, 'Отправка включена')


@bot.message_handler(commands=['count'])
def switch(message):
    id = str(message.chat.id)
    if id == '538231919':
        bot.send_message(id, count_got_files)


def post_timer():
    global status_send
    while True:
        if status_send:
            files = os.listdir('temp')
            if files:
                result = False
                while not result:
                    time.sleep(300)
                    result = send()
                bot.send_message(538231919, f'Фотка отправлена успешно, осталось {len(files)} фоток', disable_notification=True)
                time.sleep(7200)
            else:
                status_send = False
                bot.send_message(538231919, 'Фотки закончились')
        else:
            time.sleep(300)


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    global count_got_files
    id = str(message.chat.id)
    if id == '538231919':
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
