from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import sqlite3

from constants import WIN_BACKGROUND, BUTTON_STYLE_CONFIG
from login import Login
from utils import encrypt, validate_email, validate_password


def setup_db():
    connection = sqlite3.connect('passman.db')
    cursor = connection.cursor()

    query = '''
    create table if not exists password_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title text not null,
    login_url text null,
    username text not null,
    password text not null,
    is_features bool null,
    order_no integer null
    );
    '''
    cursor.execute(query)

    query = '''
    create table if not exists user_account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text not null,
    email text not null,
    username text not null,
    password text not null
    );
    '''

    cursor.execute(query)

    # sql_query = "SELECT name FROM sqlite_master WHERE type='table';"
    # cursor.execute(sql_query)
    # print(cursor.fetchall())

    connection.close()


def check_user_exists():
    connection = sqlite3.connect('passman.db')
    cursor = connection.cursor()

    cursor.execute('select * from user_account')
    user_record = cursor.fetchone()

    connection.close()

    return True if user_record else False


def delete_user():
    connection = sqlite3.connect('passman.db')
    cursor = connection.cursor()

    cursor.execute('delete from user_account')

    connection.commit()
    connection.close()


class Register:
    def __init__(self):
        setup_db()
        # delete_user()

        if check_user_exists() is True:
            Login()
            return

        self.register_window = Tk()
        self.register_window.geometry('250x380')
        self.register_window.title('Registration')
        self.register_window.resizable(False, False)
        self.register_window.config(background=WIN_BACKGROUND)

        s = ttk.Style()
        s.configure('My.TFrame', background=WIN_BACKGROUND)
        s.configure('N.Label', background=WIN_BACKGROUND)

        main_frame = ttk.Frame(self.register_window, style='My.TFrame')
        main_frame.pack(pady=20)

        title_label = ttk.Label(
            main_frame, text='Registration', foreground='#343232', style='N.Label', font=("Arial", 14, 'bold')
        )
        title_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

        self.name = StringVar()
        self.email = StringVar()
        self.username_val = StringVar()
        self.password_val = StringVar()

        name_label = ttk.Label(main_frame, text='Name', style='N.Label')
        email_label = ttk.Label(main_frame, text='Email', style='N.Label')
        username_label = ttk.Label(main_frame, text='Username', style='N.Label')
        password_label = ttk.Label(main_frame, text='Password', style='N.Label')

        name_entry = ttk.Entry(main_frame, textvariable=self.name, width=30)
        email_entry = ttk.Entry(main_frame, textvariable=self.email, width=30)
        username_entry = ttk.Entry(main_frame, textvariable=self.username_val, width=30)
        password_entry = ttk.Entry(main_frame, textvariable=self.password_val, width=30, show='*')

        register_button = Button(main_frame, text='Register', command=self.register_click)
        register_button.config(**BUTTON_STYLE_CONFIG)

        self.msg_label = ttk.Label(main_frame, foreground='red', style='N.Label')

        name_label.grid(row=1, column=0, pady=(13, 5))
        name_entry.grid(row=2, column=0,)

        email_label.grid(row=3, column=0, pady=(13, 5))
        email_entry.grid(row=4, column=0)

        username_label.grid(row=5, column=0, pady=(13, 5))
        username_entry.grid(row=6, column=0)

        password_label.grid(row=7, column=0, pady=(13, 5))
        password_entry.grid(row=8, column=0)

        for index, item in enumerate(main_frame.winfo_children()):
            item.grid_configure(sticky='w')

        register_button.grid(row=9, column=0, pady=(20, 5), sticky='ew')

        self.msg_label.grid(row=10, column=0, pady=(10, 5))



        self.register_window.bind('<Return>', self.register_click)

        self.register_window.mainloop()

    def validate_entry(self):
        validation_data = (
            (self.name, 'Name field is required.'),
            (self.email, 'Email field is required.'),
            (self.username_val, 'Username field is required.'),
            (self.password_val, 'Password field is required.'),
        )
        is_valid = True
        for entry, msg in validation_data:
            if entry.get().strip() == '':
                self.msg_label.config(text=msg)
                is_valid = False
                break

        if len(self.email.get().strip()) > 0 and validate_email(self.email.get()) is False:
            self.msg_label.config(text='Invalid email address provided.')
            is_valid = False

        if len(self.password_val.get()) > 0:
            result, message = validate_password(self.password_val.get())
            if result is False:
                self.msg_label.config(text=message)
                is_valid = False

        return is_valid

    def register_click(self, *args):
        if self.validate_entry() is False:
            return

        connection = sqlite3.connect('passman.db')
        cursor = connection.cursor()

        query = 'insert into user_account (name, email, username, password) values (?,?,?,?)'

        cursor.execute(
            query,
            (
                self.name.get().strip(),
                self.email.get().strip(),
                self.username_val.get().strip(),
                encrypt(self.password_val.get().strip())
            )
        )

        connection.commit()
        connection.close()

        messagebox.showinfo('Registration Success', 'Registration successfully done.')
        self.register_window.destroy()
        Login()


if __name__ == '__main__':
    Register()
