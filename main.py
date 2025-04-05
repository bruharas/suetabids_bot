from datetime import datetime, timedelta
from telebot import types
import telebot
import emoji
import json
import os

token = None # Введите здесь токен бота Telegram
admin = None # Введите здесь ID Telegram аккаунта админа
cooldown_file = 'user_cooldowns.json'
users_file = 'users.json'

bot = telebot.TeleBot(token)

def load_users():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file, indent=4)

try:
    with open(cooldown_file, 'r') as file:
        user_cooldowns = json.load(file)
        for user_id, last_used_str in user_cooldowns.items():
            user_cooldowns[user_id] = datetime.fromisoformat(last_used_str)
except FileNotFoundError:
    user_cooldowns = {}

def save_cooldowns():
    cooldowns_to_save = {user_id: last_used.isoformat() for user_id, last_used in user_cooldowns.items()}
    with open(cooldown_file, 'w') as file:
        json.dump(cooldowns_to_save, file)

def clean_old_cooldowns():
    global user_cooldowns
    current_time = datetime.now()
    user_cooldowns = {user_id: last_used for user_id, last_used in user_cooldowns.items()
                      if current_time - last_used < timedelta(minutes=5)}

def main_menu():
    menu = telebot.types.InlineKeyboardMarkup()
    menu.add(telebot.types.InlineKeyboardButton(text = 'Заявка', callback_data ='main_menu_bid'))
    menu.add(telebot.types.InlineKeyboardButton(text = 'Тех. поддержка', callback_data ='main_menu_support'))
    return menu

def admin_menu():
    menu = telebot.types.InlineKeyboardMarkup()
    menu.add(telebot.types.InlineKeyboardButton(text = 'Ответить по ID', callback_data ='admin_menu_answer'))
    menu.add(telebot.types.InlineKeyboardButton(text = 'Принять заявку по ID', callback_data ='admin_menu_accept_bid'))
    menu.add(telebot.types.InlineKeyboardButton(text = 'Файлы', callback_data ='admin_menu_get_files'))
    return menu

@bot.message_handler(commands=["start"])
def handler(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users:
        users[user_id] = {
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'user_alr': 0
        }
        save_users(users)
    else:
        pass
    
    btn = telebot.types.InlineKeyboardMarkup()
    btn.add(telebot.types.InlineKeyboardButton(text = 'Меню', callback_data ='btn_menu'))
    bot.send_photo(message.chat.id, open("banners/start.png", "rb"), emoji.emojize(f"""
:waving_hand: Приветствую, {message.from_user.first_name}! Добро пожаловать в бота по приёму заявок в форум клан - Суетологи.

:paperclip: Наша тема на форуме: lolz.live/threads/8310671/
"""), reply_markup=btn)

@bot.message_handler(commands=["menu"])
def handler(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users:
        users[user_id] = {
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'user_alr': 0
        }
        save_users(users)
    else:
        pass

    bot.send_photo(message.chat.id, open("banners/menu.png", "rb"), emoji.emojize(':musical_keyboard: Меню бота.'), reply_markup=main_menu())

@bot.message_handler(commands=["bid"])
def handler(message):
    user_id = str(message.from_user.id)
    users = load_users()
    status = users[user_id]["user_alr"]

    if user_id not in users:
        users[user_id] = {
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'user_alr': 0
        }
        save_users(users)
    else:
        pass
    
    if status == 1:
        bot.send_message(message.chat.id, emoji.emojize(':red_exclamation_mark: Заявка уже была ранее заполнена. Если нет, то обратитесь в поддержку.'))
        return

    btn = telebot.types.InlineKeyboardMarkup()
    btn.add(telebot.types.InlineKeyboardButton(text = 'Подать заявку', callback_data ='main_menu_bid_btn'))
    bot.send_photo(message.chat.id, open("banners/bid.png", "rb"), emoji.emojize(':red_exclamation_mark: Чтобы подать заявку в клан нажмите на кнопку ниже.'), reply_markup=btn)

@bot.message_handler(commands=["support"])
def handler(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users:
        users[user_id] = {
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'user_alr': 0
        }
        save_users(users)
    else:
        pass
    
    user_id = str(message.from_user.id)
    last_used = user_cooldowns.get(user_id)

    if last_used and datetime.now() - last_used < timedelta(minutes=5):
        bot.send_message(message.chat.id, emoji.emojize(":red_exclamation_mark: Вы недавно отправляли тикет. Подождите немного!"))
        return

    btn = telebot.types.InlineKeyboardMarkup()
    btn.add(telebot.types.InlineKeyboardButton(text = 'Отправить тикет', callback_data ='main_menu_support_btn'))
    bot.send_photo(message.chat.id, open("banners/support.png", "rb"), emoji.emojize(':red_exclamation_mark: Чтобы отправить тикет нажмите на кнопку ниже.'), reply_markup=btn)

@bot.message_handler(commands=["a"])
def handler(message):
    user_id = message.from_user.id
    if user_id == admin:
        bot.send_message(message.chat.id, "Админ панель", reply_markup=admin_menu())
    else:
        pass

@bot.callback_query_handler(func=lambda call: True)
def handler(call):
    if call.data == "btn_menu":
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_photo(call.message.chat.id, open("banners/menu.png", "rb"), emoji.emojize(':musical_keyboard: Меню бота.'), reply_markup=main_menu())
    elif call.data == "main_menu_bid":
        user_id = str(call.message.chat.id)
        users = load_users()
        status = users[user_id]["user_alr"]

        if status == 1:
            bot.send_message(call.message.chat.id, emoji.emojize(':red_exclamation_mark: Заявка уже была ранее заполнена. Если нет, то обратитесь в поддержку.'))
            return

        bot.delete_message(call.message.chat.id, call.message.id)
        btn = telebot.types.InlineKeyboardMarkup()
        btn.add(telebot.types.InlineKeyboardButton(text = 'Подать заявку', callback_data ='main_menu_bid_btn'))
        bot.send_photo(call.message.chat.id, open("banners/bid.png", "rb"), emoji.emojize(':red_exclamation_mark: Чтобы подать заявку в клан нажмите на кнопку ниже.'), reply_markup=btn)
    elif call.data == "main_menu_bid_btn":
        bot.delete_message(call.message.chat.id, call.message.id)
        msg = bot.send_message(call.message.chat.id, emoji.emojize(':red_question_mark: Хорошо, приступим к заполнению заявки. Пришлите сейчас ссылку на ваш профиль форума LOLZ. Если хотите закончить заполнение, то отмените его командой /cancel.'))
        bot.register_next_step_handler(msg, main_menu_bid_btn_func1)
    elif call.data == "main_menu_bid_btn_confirm":
        bot.send_message(admin, f"Новая заявка!\n1. Профиль: {url}\n2. Узнал: {fromq}\n3. User: {real_name} ( @{real_usrnm} - {usr_id} )\n\n#заявка")
        bot.send_message(call.message.chat.id, emoji.emojize(':check_mark_button: Заявка отправлена, ожидайте ответа администратора!'))
        user_id = str(call.message.chat.id)
        users = load_users()
        users[user_id]["user_alr"] = 1
        save_users(users)
    elif call.data == "main_menu_support":
        user_id = str(call.message.chat.id)
        last_used = user_cooldowns.get(user_id)

        if last_used and datetime.now() - last_used < timedelta(minutes=5):
            bot.send_message(call.message.chat.id, emoji.emojize(":red_exclamation_mark: Вы недавно отправляли тикет. Подождите немного!"))
            return
        
        bot.delete_message(call.message.chat.id, call.message.id)
        btn = telebot.types.InlineKeyboardMarkup()
        btn.add(telebot.types.InlineKeyboardButton(text = 'Отправить тикет', callback_data ='main_menu_support_btn'))
        bot.send_photo(call.message.chat.id, open("banners/support.png", "rb"), emoji.emojize(':red_exclamation_mark: Чтобы отправить тикет нажмите на кнопку ниже.'), reply_markup=btn)
    elif call.data == "main_menu_support_btn":
        bot.delete_message(call.message.chat.id, call.message.id)
        msg = bot.send_message(call.message.chat.id, emoji.emojize(':red_question_mark: Отправьте сообщение для администратора.'))
        bot.register_next_step_handler(msg, main_menu_support_btn_func)
    elif call.data == "admin_menu_answer":
        msg = bot.send_message(call.message.chat.id, 'Отправьте ID пользователя. Если хотите закончить заполнение, то отмените его командой /cancel.')
        bot.register_next_step_handler(msg, admin_menu_answer_func1)
    elif call.data == "admin_menu_answer_func2_confirm":
        try:
            bot.send_message(user_adm_id, emoji.emojize(f":red_exclamation_mark: Вам пришло сообщение от администратора! Вот его содержимое...\n{msg_for_user}"))
            bot.send_message(adm, "Отправлено!")
        except Exception as ex:
            bot.send_message(adm, f"Произошла ошибка при отправке: {ex}!")
    elif call.data == "admin_menu_accept_bid":
        msg = bot.send_message(call.message.chat.id, 'Отправьте ID пользователя. Если хотите закончить принятие заявки, то отмените его командой /cancel.')
        bot.register_next_step_handler(msg, admin_menu_accept_bid_func)
    elif call.data == "admin_menu_accept_bid_func1_confirm":
        try:
            bot.send_message(user_adm_id, emoji.emojize(f':check_mark_button: Ваша заявка принята! Ссылка-приглашение в чат клана (обязательно): https://t.me/+2lH7WPKTEFplOTUy'))
            bot.send_message(call.message.chat.id, "Сообщение отправлено!")
        except Exception as ex:
            bot.send_message(call.message.chat.id, f"Произошла ошибка при принятии: {ex}!")
    elif call.data == "admin_menu_get_files":
        files_temp = [f for f in os.listdir() if os.path.isfile(f)]
        files = ""
        for file in files_temp:
            files = files + f"{file}\n"
        dirs_temp = [f for f in os.listdir() if os.path.isdir(f)]
        dirs = ""
        for dir in dirs_temp:
            dirs = dirs + f"{dir}\n"
        msg = bot.send_message(call.message.chat.id, f"""
Введите название файла для выгрузки, либо /cancel для отмены команды.

```
Files:
{files}
Dirs:
{dirs}
```
""", parse_mode="Markdown")
        bot.register_next_step_handler(msg, admin_menu_get_files_func)

def admin_menu_get_files_func(message):
    file = message.text
    if "/cancel" in file:
        bot.send_message(message.chat.id, "Отменено.")
    else:
        bot.send_document(message.chat.id, open(file, "rb"))

def admin_menu_accept_bid_func(message):
    try:
        global user_adm_id
        user_adm_id = int(message.text)
    except ValueError:
        if "/cancel" in message.text:
            bot.send_message(message.chat.id, f"Отменено.")
            return
        else:
            bot.send_message(message.chat.id, "Неверный ID (ValueError). Отменено.")
            return
    btn = telebot.types.InlineKeyboardMarkup()
    btn.add(telebot.types.InlineKeyboardButton(text = 'Отправить', callback_data ='admin_menu_accept_bid_func1_confirm'))
    bot.send_message(message.chat.id, f"Подтвердите отправку уведомления о принятии заявки для пользователя ( {user_adm_id} ).", reply_markup=btn)

def admin_menu_answer_func1(message):
    try:
        global user_adm_id
        user_adm_id = int(message.text)
    except ValueError:
        if "/cancel" in message.text:
            pass
        else:
            bot.send_message(message.chat.id, f"Неверный ID (ValueError). Отменено.")
            return
    if "/cancel" in message.text:
        bot.send_message(message.chat.id, f"Отменено.")
    else:
        msg = bot.send_message(message.chat.id, f'Отправьте сообщение для пользователя ( {user_adm_id} ). Если хотите закончить заполнение, то отмените его командой /cancel.')
        bot.register_next_step_handler(msg, admin_menu_answer_func2)

def admin_menu_answer_func2(message):
    btn = telebot.types.InlineKeyboardMarkup()
    btn.add(telebot.types.InlineKeyboardButton(text = 'Отправить', callback_data ='admin_menu_answer_func2_confirm'))
    global msg_for_user
    msg_for_user = message.text
    global adm
    if "/cancel" in msg_for_user:
        bot.send_message(message.chat.id, f"Отменено.")
    else:
        adm = message.from_user.id
        bot.send_message(message.chat.id, f'Вы собираетесь отправить следущее сообщение пользователю ( {user_adm_id} )...\n{msg_for_user}', reply_markup=btn)

def main_menu_support_btn_func(message):
    clean_old_cooldowns()
    user_id = str(message.from_user.id)
    last_used = user_cooldowns.get(user_id)

    if last_used and datetime.now() - last_used < timedelta(minutes=5):
        bot.send_message(message.chat.id, emoji.emojize(":red_exclamation_mark: Вы недавно отправляли тикет. Подождите немного!"))
        return

    user_cooldowns[user_id] = datetime.now()
    save_cooldowns()

    bot.send_message(admin, f"Новый тикет!\n\nUser: {message.from_user.first_name} ( @{message.from_user.username} - {message.from_user.id} )\n\n#тикет")
    bot.forward_message(admin, message.chat.id, message.id)
    bot.send_message(message.chat.id, emoji.emojize(f":check_mark_button: Отправлено! Ожидайте ответ от администратора."))

def main_menu_bid_btn_func1(message):
    global url
    url = message.text
    if "/cancel" in url:
        bot.send_message(message.chat.id, emoji.emojize(f":red_exclamation_mark: Отменено."))
    else:
        msg = bot.send_message(message.chat.id, emoji.emojize(f":red_question_mark: Откуда узнали о нас? Если хотите закончить заполнение, то отмените его командой /cancel."))
        bot.register_next_step_handler(msg, main_menu_bid_btn_func2)

def main_menu_bid_btn_func2(message):
    btn = telebot.types.InlineKeyboardMarkup()
    btn.add(telebot.types.InlineKeyboardButton(text = 'Отправить', callback_data ='main_menu_bid_btn_confirm'))
    global fromq
    fromq = message.text
    global real_usrnm
    real_usrnm = message.from_user.username
    global real_name
    real_name = message.from_user.first_name
    global usr_id
    usr_id = message.from_user.id
    if "/cancel" in fromq:
        bot.send_message(message.chat.id, emoji.emojize(f":red_exclamation_mark: Отменено."))
    else:
        msg = bot.send_message(message.chat.id, emoji.emojize(f"""
❗ Проверьте заполненную заявку:
1. Ссылка на профиль форума: {url}
2. Откуда узнали о нас: {fromq}
"""), reply_markup=btn)

bot.infinity_polling()