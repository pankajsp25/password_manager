from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import sqlite3

from constants import WIN_BACKGROUND, BUTTON_STYLE_CONFIG
from dashboard import Dashboard
from utils import decrypt


class Login:
    def __init__(self):
        self.login_window = Tk()
        self.login_window.geometry('300x260')
        self.login_window.title('Login')
        self.login_window.resizable(False, False)
        self.login_window.config(background=WIN_BACKGROUND)

        s = ttk.Style()
        s.configure('My.TFrame', background=WIN_BACKGROUND)
        s.configure('N.Label', background=WIN_BACKGROUND)

        main_frame = ttk.Frame(self.login_window, style='My.TFrame')
        main_frame.pack(pady=20)

        self.username_val = StringVar()
        self.password_val = StringVar()

        title_label = ttk.Label(main_frame, text='Account Login', foreground='#343232', style='N.Label', font=("Arial", 15, 'bold'))
        title_label.grid(row=0, column=0, sticky='w', pady=(0, 20))

        username_label = ttk.Label(main_frame, text='Username', style='N.Label')
        password_label = ttk.Label(main_frame, text='Password', style='N.Label')
        username_entry = ttk.Entry(main_frame, textvariable=self.username_val, width=30)
        password_entry = ttk.Entry(main_frame, textvariable=self.password_val, width=30, show='*')

        login_button = Button(main_frame, text='Login', command=self.login_click)
        login_button.config(**BUTTON_STYLE_CONFIG)

        username_label.grid(row=1, column=0, sticky='w', pady=(0, 5))
        username_entry.grid(row=2, column=0)
        password_label.grid(row=3, column=0, sticky='w', pady=(10, 5))
        password_entry.grid(row=4, column=0)
        login_button.grid(row=5, column=0, sticky='ew', pady=15)

        username_entry.focus()

        self.login_window.bind('<Return>', self.login_click)
        self.login_window.mainloop()

    def check_credentials(self) -> bool:
        connection = sqlite3.connect('passman.db')
        cursor = connection.cursor()

        cursor.execute('select * from user_account where username=?', (self.username_val.get(),))
        user_record = cursor.fetchone()
        if not user_record:
            messagebox.showerror('Login failed', 'Invalid username provided.')
            return False

        if self.password_val.get() == decrypt(user_record[4]):
            return True
        else:
            messagebox.showerror('Login failed', 'Invalid password provided.')
            self.password_val.set('')
            return False

    def login_click(self, *args):
        if self.check_credentials() is True:
            self.login_window.destroy()
            Dashboard()
