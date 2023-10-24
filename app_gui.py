import tkinter as tk
import threading
import webbrowser
from app import app

def open_browser():
    webbrowser.open_new_tab('http://127.0.0.1:5000')

def run_flask():
    app.run()

root = tk.Tk()
root.title('Запуск сайта')
t1 = threading.Thread(target=run_flask, daemon=True)

button = tk.Button(root, text=" Запустить локально ", command=lambda: [t1.start(), open_browser()])

text = """
Для запуска нажмите на кнопку "Запустить локально"
Если сайт автоматически не открылся, то необходимо вручную ввести в браузере адрес сайта: http://127.0.0.1:5000
Для выключения локального сервера закройте это приложение

--------------------
Использование сайта:
* Просмотр индексов:
   Для ввода нескольких параметров (несколько марок/несколько моделей) необходимо в соответствующей форме с помощью ctrl+лкм выделить нужные параметры
* Регистрация:
   1) Для входа на сайт как сторонний пользователь необходимо зарегистрироваться в базе данных: "Вход на сайт" -> "Создать новый аккаунт"
   2) Для входа в качестве дилера (дилер с id=1 из данных sale_data.csv) необходимо в поле входа ввести следующие данные:             
"""

data = """почта: dealer@m.com
пароль: d12345"""

label = tk.Label(text=text)
text_widget = tk.Text(root, width=20, height=2)
text_widget.insert(tk.END, data)
label.pack()
text_widget.pack()

button.pack()
root.mainloop()
