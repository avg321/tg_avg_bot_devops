import logging,re,paramiko,io,psycopg2,os
from psycopg2 import Error
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)
load_dotenv()
TOKEN = os.getenv("TOKEN")
# Определяем константы этапов разговора
APT1, APT2 = range(2)

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def select(selectcmd):
    connection = None

    try:
        connection = psycopg2.connect(user=os.getenv("DB_USER"),
                                      password=os.getenv("DB_PASSWORD"),
                                      host=os.getenv("DB_HOST"),
                                      port=os.getenv("DB_PORT"),
                                      database=os.getenv("DB_DATABASE"))

        cursor = connection.cursor()
        cursor.execute(selectcmd)
        data = cursor.fetchall()
        for row in data:
            print(row)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
    return data  # возвращаем ответ системы

def insert(insertcmd):
    connection = None

    try:
        connection = psycopg2.connect(user=os.getenv("DB_USER"),
                                      password=os.getenv("DB_PASSWORD"),
                                      host=os.getenv("DB_HOST"),
                                      port=os.getenv("DB_PORT"),
                                      database=os.getenv("DB_DATABASE"))
        cursor = connection.cursor()
        cursor.execute(insertcmd)
        connection.commit()
        logging.info("Команда успешно выполнена")
        data = "Запись в базу успешно выполнена"
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        data ="Ошибка. Запись в базу не выполнена!"
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")
    return data # возвращаем ответ системы
def sshmon(cmd): #подключение к хосту по ssh и выполнение необходимой команды
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  # client.connect(hostname=host, username=username, password=password, port=port)
    client.connect(hostname=os.getenv("RM_HOST"), username=os.getenv("RM_USER"), password=os.getenv("RM_PASSWORD"), port=os.getenv("RM_PORT"))
    stdin, stdout, stderr = client.exec_command(cmd)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data #возвращаем ответ системы
def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!\n'
                              f'Для помощи введи /help')


def helpCommand(update: Update, context):
    update.message.reply_text('/findPhoneNumbers - поиск номеров телефонов в тексте\n'
                              '/findEmails - поиск адресов электронной почты в тексте\n'
                              '/verify_password - проверка сложности пароля\n'
                              '/get_release - данные о релизе системы\n'
                              '/get_uname - данные о системе\n'
                              '/get_uptime - данные о времени работы\n'
                              '/get_df -  данные о файловой системе\n'
                              '/get_free - данные об оперативной памяти\n'
                              '/get_mpstat - данные о производительности системы\n'
                              '/get_w - данные о работающих пользователях\n'
                              '/get_auths - данные о последних 10 входах в систему\n'
                              '/get_critical - данные о последних 5 критических событиях\n'
                              '/get_ps - данные о запущенных процессах\n'
                              '/get_ss - данные об используемых портах\n'
                              '/get_apt_list - данные об установленных пакетах\n'
                              '/get_services - данные о запущенных сервисах\n'
                              '/get_repl_logs - вывод логов репликации \n'
                              '/get_emails - вывод почтовых адресов из БД \n'
                              '/get_phone_numbers - вывод номеров телефонов из БД \n')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска почтовых адресов: ')

    return 'findEmails'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки его сложности: ')

    return 'verifyPassword'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = r"((\+7)|8)(\(|\ \(|\-|\ )?\d{3}(\)|\)\ |\-|\ )?\d{3}(\ |\-)?\d{2}(\ |\-)?\d{2}"

    matches = re.finditer(phoneNumRegex, user_input) # поиск телефонных номеров

    phoneNumbers = ''
    for matchNum, match in enumerate(matches, start=1):
        phoneNumbers += f'{matchNum}. {match.group()}\n'
        data = insert(f'INSERT INTO phone_tab (phone) VALUES (\' {match.group()} \');' )
    if phoneNumbers == '':  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END  # Завершаем работу обработчика диалога
    else:
        update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю.
        update.message.reply_text(data)
        return ConversationHandler.END


def findEmails(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) почтового адреса

    EmailsRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')  # поиск почтовых адресов

    EmailsList = EmailsRegex.findall(user_input)  # Ищем почтовый адрес

    if not EmailsList:  # Обрабатываем случай, когда почтовых адресов нет
        update.message.reply_text('Почтовые адреса не найдены')
        return  # Завершаем выполнение функции

    Emails = ''  # Создаем строку, в которую будем записывать почтовые адреса
    for i in range(len(EmailsList)):
        Emails += f'{i + 1}. {EmailsList[i]}\n'  # Записываем очередной почтовый адрес
        data = insert(f'INSERT INTO email_tab (email) VALUES (\' {EmailsList[i]} \');')
        print(EmailsList[i])
    update.message.reply_text(Emails)  # Отправляем сообщение
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def verifyPassword(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий пароль

    PasswordRegex = re.compile(r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)(?=.*[@$!%*#?&])[0-9a-zA-Z@$!%*#?&]{8,}$')  # проверка сложности пароля

    if bool(PasswordRegex.match(user_input)):  # Если пароль соответствует требованиям
        update.message.reply_text("Пароль сложный")
    else:
        update.message.reply_text('Пароль простой')

    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_release(update: Update, context): #данные о релизе ОС
    data = sshmon('lsb_release -a')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_uname(update: Update, context): #данные о систем
    data = sshmon('uname')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_uptime(update: Update, context): #данные о времени работы системы
    data = sshmon('uptime -p')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_df(update: Update, context): #данные о файловой системе
    data = sshmon('df -h')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_free(update: Update, context): #данные об оперативной памяти
    data = sshmon('free -h')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_mpstat(update: Update, context): #данные о производительности системы
    data = sshmon('mpstat')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_w(update: Update, context): #данные о работающих пользователях
    data = sshmon('w')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_auths(update: Update, context): #данные о последних 10 входах в систему
    data = sshmon('last -10')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога
def get_critical(update: Update, context): #данные о последних 5 критических событиях системы
    data = sshmon('journalctl -p 2 -n 5')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_ps(update: Update, context): #данные о запущенных процессах
    data = sshmon('ps')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_ss(update: Update, context):
    data = sshmon('ss -t -a')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_services(update: Update, context): #данные об используемых портах
    data = sshmon('service --status-all')
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


#def echo(update: Update, context):
  #  update.message.reply_text(update.message.text)

def get_apt_list(update: Update, context):
    # Список кнопок для ответа
    reply_keyboard = [['Вывести список всех приложений', 'Вывести конкретное приложение', ]]
    # Создаем простую клавиатуру для ответа
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    # Начинаем разговор с вопроса
    update.message.reply_text('Выбирите какие приложения необходимо отразить',
    reply_markup=markup_key,)
    return APT1

def get_apt1(update: Update, context):
    user_input = update.message.text
    if user_input == 'Вывести список всех приложений':
        data = sshmon('apt list')
        #print (data)
        update.message.reply_document(io.StringIO(data), filename='apt list.txt')
        # Завершаем работу обработчика диалога
        return ConversationHandler.END
    else:
    # Отвечаем на то что пользователь рассказал.
        update.message.reply_text('Введите приложение, информацию по которому необходимо вывести')
    # Заканчиваем разговор.
        return APT2

def get_apt2(update: Update, context):
    user_input = update.message.text
    command_apt_list = 'apt list ' + user_input
    data = sshmon(command_apt_list)
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_repl_logs(update: Update, context): #логи синхронизации
    data = sshmon('docker logs db_image 2>&1 | grep "replica"')
    print(data)
    update.message.reply_document(io.StringIO(data), filename='repl_log.txt')
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_emails(update: Update, context): #вывод emails
    data = select('SELECT * FROM email_tab;')
    print(data)
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def get_phone_numbers(update: Update, context): #вывод телефонов
    data = select('SELECT * FROM phone_tab;')
    print(data)
    update.message.reply_text(data)
    return ConversationHandler.END  # Завершаем работу обработчика диалога
def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('findEmails', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
        },
        fallbacks=[]
    )
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )
    convHandlerGetAptList = ConversationHandler(
        # точка входа в диалог
        entry_points=[CommandHandler('get_apt_list', get_apt_list)],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            APT1: [MessageHandler(Filters.regex('^((Вывести список всех приложений)|(Вывести конкретное приложение))$'), get_apt1)],
            APT2: [MessageHandler(Filters.text & ~Filters.command, get_apt2)],
        },
        # точка выхода из диалога
        fallbacks=[],
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(CommandHandler("get_services", get_services))
    # Регистрируем обработчик текстовых сообщений
    #dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
user@ansible:~/bot$