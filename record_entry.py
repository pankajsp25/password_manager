import sqlite3

from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from constants import PASS_MASK_KEY, WIN_BACKGROUND, BUTTON_STYLE_CONFIG
from utils import encrypt, decrypt


class RecordEntry:
    def __init__(self, master_window, fetch_data, record_id=None):
        self.fetch_data = fetch_data
        self.record_id = record_id

        self.record_entry_window = Toplevel(master_window)
        self.record_entry_window.geometry('370x280')
        self.record_entry_window.title('Record Entry')
        self.record_entry_window.transient(master_window)
        self.record_entry_window.config(background=WIN_BACKGROUND)

        self.record_entry_window.resizable(False, False)

        s = ttk.Style()
        s.configure('My.TFrame', background=WIN_BACKGROUND)
        s.configure('N.Label', background=WIN_BACKGROUND)

        frame = ttk.Frame(self.record_entry_window, style='My.TFrame')
        frame.pack(pady=15)

        self.is_featured = BooleanVar(value=False)

        title_lbl = ttk.Label(frame, text='Title', anchor='w', style='N.Label')
        title_lbl.grid(row=0, column=0, sticky='w')

        self.title_entry = ttk.Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1)

        login_url_lbl = ttk.Label(frame, text='Link URL', anchor='w', style='N.Label')
        login_url_lbl.grid(row=1, column=0, sticky='w')

        self.login_url_entry = ttk.Entry(frame, width=30)
        self.login_url_entry.grid(row=1, column=1)

        username_lbl = ttk.Label(frame, text='Username', style='N.Label')
        username_lbl.grid(row=2, column=0, sticky='w')

        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.grid(row=2, column=1)

        password_lbl = ttk.Label(frame, text='Password', style='N.Label')
        password_lbl.grid(row=3, column=0, sticky='w')

        self.password_entry = ttk.Entry(frame, width=30)
        self.password_entry.grid(row=3, column=1)

        self.featured_check = Checkbutton(
            frame, variable=self.is_featured, background=WIN_BACKGROUND,
            text='Mark as featured record', onvalue=True, offvalue=False,
        )
        self.featured_check.grid(row=4, column=0, columnspan=2, sticky='w')

        if record_id:
            self.fetch_record(record_id)
            update_button = Button(frame, text='Update', command=self.update_record)
            update_button.grid(row=5, column=0, columnspan=2, sticky='ew')
            update_button.config(**BUTTON_STYLE_CONFIG)
            self.record_entry_window.bind('<Return>', self.update_record)
        else:
            add_button = Button(frame, text='Add', command=self.create_entry)
            add_button.grid(row=5, column=0, columnspan=2, sticky='ew')
            add_button.config(**BUTTON_STYLE_CONFIG)
            self.record_entry_window.bind('<Return>', self.create_entry)

        self.msg_label = ttk.Label(frame, foreground='red', style='N.Label')
        self.msg_label.grid(row=6, column=0, columnspan=2)

        for item in frame.winfo_children():
            item.grid_configure(padx=7, pady=7)

    def validate_entry(self):
        validation_data = (
            (self.title_entry, 'Title field is required.'),
            (self.login_url_entry, 'Login URL field is required.'),
            (self.username_entry, 'Username field is required.'),
            (self.password_entry, 'Password field is required.'),
        )
        is_valid = True
        for entry, msg in validation_data:
            if entry.get().strip() == '':
                self.msg_label.config(text=msg)
                entry.focus()
                is_valid = False
                break

        return is_valid

    def create_entry(self, *args):
        if self.validate_entry() is False:
            return

        connection = sqlite3.connect('passman.db')
        cursor = connection.cursor()

        query = '''
        insert into password_records (title, login_url, username, password, is_features) values (?,?,?,?,?)
        '''

        title = self.title_entry.get()
        login_url = self.login_url_entry.get()
        username = self.username_entry.get()
        password = encrypt(self.password_entry.get())

        cursor.execute(query, (title, login_url, username, password, self.is_featured.get()))

        cursor.execute("select max(id) from password_records;")
        max_id = cursor.fetchone()
        print(f'max_id: {max_id}')

        connection.commit()
        connection.close()

        self.record_entry_window.destroy()
        messagebox.showinfo('Record Added', 'Record added successfully.')

        self.fetch_data()

    def fetch_record(self, record_id):
        connection = sqlite3.connect('passman.db')
        cursor = connection.cursor()

        cursor.execute("select * from password_records where id=?;", (record_id,))

        record_data = cursor.fetchone()
        print(f'record_data: {record_data}')
        self.title_entry.insert(END, record_data[1])
        self.login_url_entry.insert(END, record_data[2])
        self.username_entry.insert(END, record_data[3])
        self.password_entry.insert(END, decrypt(record_data[4]))
        self.is_featured.set(record_data[5])

    def update_record(self, *args):
        if self.validate_entry() is False:
            return

        connection = sqlite3.connect('passman.db')
        cursor = connection.cursor()

        query = '''
        update password_records set title=?, login_url=?, username=?, password=?, is_features=?
        where id=?;
        '''

        params = (
            self.title_entry.get(),
            self.login_url_entry.get(),
            self.username_entry.get(),
            encrypt(self.password_entry.get()),
            self.is_featured.get(),
            self.record_id
        )

        cursor.execute(query, params)

        connection.commit()
        connection.close()

        self.record_entry_window.destroy()

        messagebox.showinfo("Update Conformation", "Record updated successfully.")

        self.fetch_data()

        # selected_item = self.data_treeview.selection()[0]
        # self.data_treeview.item(selected_item, text=record_id, values=params[:-1])
