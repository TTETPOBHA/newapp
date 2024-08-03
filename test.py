import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.storage.jsonstore import JsonStore
import psycopg2
import random
import smtplib
from email.mime.text import MIMEText


import logging
logging.basicConfig(level=logging.DEBUG)
# Информация о базе данных (замените на ваши данные)
DATABASE = "telegram_bot" 
USER = "postgres"
PASSWORD = "12123434"
HOST = "localhost"  # Обычно 'localhost' для локальной базы данных
PORT = "5432"

# Информация о авторизации
store = JsonStore('user_data.json')

def send_email(email, code):
    try:
        smtp_server = 'smtp.yandex.ru'
        smtp_port = 465  # Порт для SSL
        sender_email = 'myrov.dmit@yandex.ru'  # Ваш адрес Yandex
        sender_password = 'lpngniomnvitcyok'  # Ваш пароль Yandex

        msg = MIMEText(f'Ваш код подтверждения: {code}')
        msg['Subject'] = 'Восстановление пароля'
        msg['From'] = sender_email
        msg['To'] = email

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:  # Используем SMTP_SSL
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())

        print(f"Письмо с кодом отправлено на {email}")
        return True

    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
        return False











class LoginForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20

        self.add_widget(Label(text="Вход", font_size=24, color=(0.2, 0.5, 1, 1)))

        self.email_input = TextInput(hint_text='Почта', font_size=16, size_hint_y=None, height=40,
                                      background_color=(0.9, 0.9, 0.9, 1))
        self.add_widget(self.email_input)

        self.password_input = TextInput(hint_text='Пароль', font_size=16, size_hint_y=None, height=40,
                                        password=True, background_color=(0.9, 0.9, 0.9, 1))
        self.add_widget(self.password_input)

        self.login_button = Button(text="Войти", font_size=18, background_color=(0.2, 0.5, 1, 1),
                                    color=(1, 1, 1, 1), size_hint_y=None, height=50)
        self.login_button.bind(on_press=self.login)
        self.add_widget(self.login_button)

        self.message_label = Label(text="", font_size=14, color=(1, 0, 0, 1))
        self.add_widget(self.message_label)

    def login(self, instance):
        email = self.email_input.text
        password = self.password_input.text

        # Подключение к базе данных
        conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        cur = conn.cursor()

        # Проверка в базе данных
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            # Успешная авторизация
            store.put('user_data', logged_in=True, user_id=user[0])
            self.message_label.text = ""

            # Получаем доступ к MyApp и вызываем метод для перехода
            app = App.get_running_app() 
            app.go_to_main_menu()
        else:
            # Неверные данные
            self.message_label.text = "Неверный логин или пароль"


class RegistrationForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20
        self.size_hint_y = 1
        
        self.add_widget(Label(text="Регистрация", font_size=24, color=(0.2, 0.5, 1, 1)))

        self.name_input = TextInput(hint_text='Имя', font_size=16, size_hint_y=None, height=40,
                                     background_color=(0.9, 0.9, 0.9, 1))
        self.add_widget(self.name_input)

        self.email_input = TextInput(hint_text='Почта', font_size=16, size_hint_y=None, height=40,
                                      background_color=(0.9, 0.9, 0.9, 1))
        self.add_widget(self.email_input)

        self.password_input = TextInput(hint_text='Пароль', font_size=16, size_hint_y=None, height=40,
                                        password=True, background_color=(0.9, 0.9, 0.9, 1))
        self.add_widget(self.password_input)

        self.register_button = Button(text="Зарегистрироваться", font_size=18, background_color=(0.2, 0.5, 1, 1),
                                        color=(1, 1, 1, 1), size_hint_y=None, height=50)
        self.register_button.bind(on_press=self.register_user)
        self.add_widget(self.register_button)

        # Добавляем изображение QR-кода
        self.qr_code_image = Image(source='temp_qr.png', size_hint=(None, None), size=(200, 200))
        self.add_widget(self.qr_code_image)

        self.message_label = Label(text="", font_size=14, color=(1, 0, 0, 1))
        self.add_widget(self.message_label)

    def register_user(self, *args):
        name = self.name_input.text
        email = self.email_input.text
        password = self.password_input.text

        if not all([name, email, password]):
            self.message_label.text = "Заполните все поля"
            return

        try:
            # Генерация случайного id длиной 9 символов
            user_id = ''.join(random.choice('0123456789') for _ in range(9))  

            # Подключение к базе данных
            conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
            cur = conn.cursor()

            # Вставка данных пользователя в базу данных (включая id и balance)
            cur.execute("INSERT INTO users (id, username, email, password, balance) VALUES (%s, %s, %s, %s, %s)",
                        (user_id, name, email, password, 0.00))

            conn.commit()
            cur.close()
            conn.close()

            self.message_label.text = "Регистрация прошла успешно!"
            # Переключаемся на экран входа после регистрации
            self.parent.parent.current = 'login'  

        except Exception as e:
            self.message_label.text = f"Ошибка при регистрации: {str(e)}"


class SupportScreenFromStart(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'support_from_start'

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text="Поддержка (из стартового экрана)", font_size=24))

        email_label = Label(text="Почта для связи: lalala@mail.ru", font_size=18)
        layout.add_widget(email_label)

        telegram_label = Label(text="Telegram для связи: @lala", font_size=18)
        layout.add_widget(telegram_label)

        # Кнопка "Вернуться в главное меню"
        back_button = Button(text="Вернуться в главное меню", font_size=18)
        back_button.bind(on_press=self.go_to_start_screen)  # Изменено на go_to_start_screen
        layout.add_widget(back_button)

        self.add_widget(layout)

            # Кнопка "Восстановить пароль" (заглушка)
        restore_password_button = Button(text="Восстановить пароль", font_size=18)
        restore_password_button.bind(on_press=self.restore_password)  # Добавьте обработчик
        layout.add_widget(restore_password_button)

        # ... (остальной код класса SupportScreenFromStart)


    def restore_password(self, instance):
        app = App.get_running_app()
        app.root.current = 'restore_password'  # Используем существующий экземпляр
    
    
    def go_to_start_screen(self, instance):
        self.parent.current = 'start'  # Изменено на 'start'

class SupportScreenFromMainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'support_from_main_menu'

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text="Поддержка (из главного меню)", font_size=24))

        email_label = Label(text="Почта для связи: lalala@mail.ru", font_size=18)
        layout.add_widget(email_label)

        telegram_label = Label(text="Telegram для связи: @lala", font_size=18)
        layout.add_widget(telegram_label)

                # Кнопка "Изменить пароль" (заглушка)
        change_password_button = Button(text="Изменить пароль", font_size=18)
        change_password_button.bind(on_press=self.change_password)
        layout.add_widget(change_password_button)
        
        # Кнопка "Вернуться в главное меню"
        back_button = Button(text="Вернуться в главное меню", font_size=18)
        back_button.bind(on_press=self.go_to_main_menu)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_to_main_menu(self, instance):
        self.parent.current = 'main_menu'

    def change_password(self, instance):
        # Здесь будет логика изменения пароля (пока заглушка)
        print("Изменение пароля (заглушка)")
        
        
class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main_menu'

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text="Главное меню", font_size=24))

        balance_button = Button(text="Баланс", font_size=18)
        balance_button.bind(on_press=lambda x: self.open_screen('balance'))
        layout.add_widget(balance_button)

        purchases_button = Button(text="Мои покупки", font_size=18)
        purchases_button.bind(on_press=lambda x: self.open_screen('purchases'))
        layout.add_widget(purchases_button)

        products_button = Button(text="Товары", font_size=18)
        products_button.bind(on_press=lambda x: self.open_screen('products'))
        layout.add_widget(products_button)

        # Кнопка поддержки
        support_button = Button(text="Поддержка", font_size=18)
        support_button.bind(on_press=lambda x: self.open_screen('support'))
        layout.add_widget(support_button)
        # Кнопка выхода
        logout_button = Button(text="Выйти", font_size=18)
        logout_button.bind(on_press=self.logout)
        layout.add_widget(logout_button)

        self.add_widget(layout)

    def open_screen(self, screen_name):
        if screen_name == 'balance':
            # Создаем экран баланса и переходим на него
            balance_screen = BalanceScreen()
            self.parent.add_widget(balance_screen)
            self.parent.current = 'balance'
        elif screen_name == 'support':
            # Создаем экран поддержки и переходим на него
            support_screen = SupportScreenFromMainMenu()  # Изменено на SupportScreenFromMainMenu
            self.parent.add_widget(support_screen)
            self.parent.current = 'support_from_main_menu'  # Изменено на 'support_from_main_menu'
        elif screen_name == 'purchases':
            # Создаем экран покупок и переходим на него
            purchases_screen = PurchasesScreen()
            self.parent.add_widget(purchases_screen)
            self.parent.current = 'purchases'
        else:
            print(f"Переход на экран: {screen_name}")
        
    def logout(self, instance):
        store.put('user_data', logged_in=False)
        app = App.get_running_app()
        app.root.current = 'start'  # Переход на начальный экран
        
        
class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'start'

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        image = Image(source='background.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(image)

        registration_button = Button(text="Регистрация", font_size=18)
        registration_button.bind(on_press=lambda x: self.open_screen('registration'))
        layout.add_widget(registration_button)

        login_button = Button(text="Вход", font_size=18)
        login_button.bind(on_press=lambda x: self.open_screen('login'))
        layout.add_widget(login_button)

        support_button = Button(text="Поддержка", font_size=18)
        support_button.bind(on_press=lambda x: self.open_screen('support'))
        layout.add_widget(support_button)

        self.add_widget(layout)
        
    def open_screen(self, screen_name):
        sm = self.parent
        if screen_name == 'support':
            screen_name = 'support_from_start'  # Изменено на 'support_from_start'
        sm.current = screen_name  # <<<  Устанавливаем экран только один раз!
        
class BalanceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'balance'

        # Получаем ID пользователя из хранилища
        user_id = store.get('user_data')['user_id']

        # Подключаемся к базе данных и получаем баланс
        conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
        balance = cur.fetchone()[0]  # Получаем значение баланса
        cur.close()
        conn.close()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Вывод баланса
        balance_label = Label(text=f"Ваш баланс: {balance}", font_size=24)
        layout.add_widget(balance_label)

        # Поле ввода суммы
        self.amount_input = TextInput(hint_text="Введите сумму для пополнения", font_size=16)
        layout.add_widget(self.amount_input)

        # Кнопка пополнения (заглушка)
        replenish_button = Button(text="Пополнить", font_size=18)
        replenish_button.bind(on_press=self.replenish)
        layout.add_widget(replenish_button)

        # Лейбл для сообщения о недоступности пополнения
        self.message_label = Label(text="", font_size=14, color=(1, 0, 0, 1))
        layout.add_widget(self.message_label)

        self.add_widget(layout)

    def replenish(self, instance):
        self.message_label.text = "В настоящий момент пополнение недоступно"      
    
    
class PurchasesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'purchases'

        # Получаем ID пользователя из хранилища
        user_id = store.get('user_data')['user_id']

        # Подключаемся к базе данных и получаем имя пользователя
        conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        username = cur.fetchone()[0]
        cur.close()
        conn.close()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Вывод имени пользователя
        username_label = Label(text=f"Пользователь: {username}", font_size=24)
        layout.add_widget(username_label)

        # Сообщение об отсутствии покупок
        no_purchases_label = Label(text="Вы ещё не совершали покупки", font_size=18)
        layout.add_widget(no_purchases_label)

        # Кнопка "Вернуться в главное меню"
        back_button = Button(text="Вернуться в главное меню", font_size=18)
        back_button.bind(on_press=self.go_to_main_menu)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_to_main_menu(self, instance):
        self.parent.current = 'main_menu'   
    
    
class RestorePasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'restore_password'
        self.code = None  # Добавляем атрибут для хранения кода
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Заголовок
        title_label = Label(text="Для сброса пароля введите почту, привязанную к аккаунту", font_size=18)
        layout.add_widget(title_label)

        # Поле ввода почты
        self.email_input = TextInput(hint_text="Введите свою почту", font_size=16)
        layout.add_widget(self.email_input)

        # Кнопка "Отправить" (пока заглушка)
        send_button = Button(text="Отправить", font_size=18)
        send_button.bind(on_press=self.send_reset_email)
        layout.add_widget(send_button)

        # Кнопка "Вернуться в главное меню"
        back_button = Button(text="Вернуться в главное меню", font_size=18)
        back_button.bind(on_press=self.go_to_start_screen)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def send_reset_email(self, instance):
        email = self.email_input.text

        # Генерация кода подтверждения
        self.code = ''.join(random.choice('0123456789') for _ in range(6))

        if send_email(email, self.code):
            app = App.get_running_app()
            app.go_to_code_input(email)  
        else:
            # Обработка ошибки отправки
            print("Ошибка отправки письма")

    def go_to_start_screen(self, instance):
        self.parent.current = 'start'  # Изменено на 'start'   
        
class CodeInputScreen(Screen):
    def __init__(self, email, **kwargs):
        super().__init__(**kwargs)
        self.name = 'code_input'
        self.email = email  # Сохраняем email

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Заголовок
        title_label = Label(text="Введите код из письма", font_size=18)
        layout.add_widget(title_label)

        # Поле ввода кода
        self.code_input = TextInput(hint_text="Введите код", font_size=16)
        layout.add_widget(self.code_input)

        # Кнопка "Подтвердить"
        confirm_button = Button(text="Подтвердить", font_size=18)
        confirm_button.bind(on_press=self.confirm_code)
        layout.add_widget(confirm_button)

        # Лейбл для сообщения об ошибке
        self.message_label = Label(text="", font_size=14, color=(1, 0, 0, 1))
        layout.add_widget(self.message_label)

        self.add_widget(layout)

    def confirm_code(self, instance):
        entered_code = self.code_input.text
        restore_password_screen = self.parent.get_screen('restore_password')

        if entered_code == restore_password_screen.code:
            app = App.get_running_app()
            app.go_to_change_password(self.email)
        else:
            # Код неверный
            self.message_label.text = "Неверный код"

class ChangePasswordScreen(Screen):
    def __init__(self, email=None, **kwargs):  # email теперь необязательный
        super().__init__(**kwargs)
        self.name = 'change_password'
        self.email = email

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Заголовок
        title_label = Label(text="Изменение пароля", font_size=18)
        layout.add_widget(title_label)

        # Поле ввода нового пароля
        self.new_password_input = TextInput(hint_text="Новый пароль", font_size=16, password=True)
        layout.add_widget(self.new_password_input)

        # Поле ввода подтверждения нового пароля
        self.confirm_password_input = TextInput(hint_text="Подтвердите пароль", font_size=16, password=True)
        layout.add_widget(self.confirm_password_input)

        # Кнопка "Сохранить"
        save_button = Button(text="Сохранить", font_size=18)
        save_button.bind(on_press=self.save_password)
        layout.add_widget(save_button)
        
                # Кнопка "Вернуться в главное меню"
        back_button = Button(text="Вернуться в главное меню", font_size=18)
        back_button.bind(on_press=self.go_to_main_menu)
        layout.add_widget(back_button)
        
        
        # Лейбл для сообщения об ошибке
        self.message_label = Label(text="", font_size=14, color=(1, 0, 0, 1))
        layout.add_widget(self.message_label)

        self.add_widget(layout)

    def save_password(self, instance):
        new_password = self.new_password_input.text
        confirm_password = self.confirm_password_input.text
        print("Email в save_password:", self.email)  # Добавьте эту строку
        if new_password == confirm_password:
            # Пароли совпадают, обновляем пароль в базе данных
            try:
                conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
                cur = conn.cursor()
                cur.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, self.email))
                conn.commit()
                cur.close()
                conn.close()


                logging.debug(f"Updating password for email: {self.email}")
                logging.debug(f"New password: {new_password}")
                logging.debug(f"SQL query: UPDATE users SET password = {new_password} WHERE email = {self.email}")
            except Exception as e:
                self.message_label.text = f"Ошибка при обновлении пароля: {str(e)}"
        else:
            # Пароли не совпадают
            self.message_label.text = "Пароли не совпадают"    
        
    def go_to_main_menu(self, instance):
        self.parent.current = 'main_menu'
        
        
        
class MyApp(App):
    
    
    def go_to_code_input(self, email):
         # Устанавливаем email для экрана ввода кода
        self.code_input_screen.email = email
        self.root.current = 'code_input'
    def build(self):
        sm = ScreenManager()

        # Экран запуска
        start_screen = StartScreen()
        sm.add_widget(start_screen)

        # Экран регистрации (добавляем только один раз)
        registration_screen = Screen(name='registration')
        registration_screen.add_widget(RegistrationForm())
        sm.add_widget(registration_screen)

        # Экран входа
        login_screen = Screen(name='login')
        login_screen.add_widget(LoginForm())
        sm.add_widget(login_screen)

        # Экран главного меню
        main_menu_screen = MainMenuScreen()
        sm.add_widget(main_menu_screen)

        
        # Экран поддержки из стартового экрана
        support_screen_from_start = SupportScreenFromStart()
        sm.add_widget(support_screen_from_start)

        # Экран поддержки из главного меню
        support_screen_from_main_menu = SupportScreenFromMainMenu()
        sm.add_widget(support_screen_from_main_menu)
        
        # Создаем экземпляры экранов для восстановления пароля и смены пароля
        self.restore_password_screen = RestorePasswordScreen()
        self.code_input_screen = CodeInputScreen(email=None)  # email будет передан позже
        self.change_password_screen = ChangePasswordScreen()  # Не передаем email здесь

        # Добавляем экраны в ScreenManager
        sm.add_widget(self.restore_password_screen)
        sm.add_widget(self.code_input_screen)
        sm.add_widget(self.change_password_screen)
        

        
        # Проверка авторизации
        if store.exists('user_data') and store.get('user_data')['logged_in']:
            sm.current = 'main_menu'
        else:
            sm.current = 'start'

        return sm
    
    # Метод для перехода на главное меню
    def go_to_main_menu(self):
        self.root.current = 'main_menu'
        
        
        # Метод для перехода на экран смены пароля
    def go_to_change_password(self, email):
        # Устанавливаем email для экрана смены пароля
        self.change_password_screen.email = email
        self.root.current = 'change_password'

if __name__ == '__main__':
    MyApp().run()