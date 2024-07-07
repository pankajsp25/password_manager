import sqlite3
import clipboard

from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from constants import PASS_MASK_KEY, WIN_BACKGROUND
from record_entry import RecordEntry
from utils import decrypt


class Dashboard:
    def __init__(self):
        self.dashboard_window = Tk()
        self.dashboard_window.geometry('850x365')
        self.dashboard_window.title('Password Dashboard')
        self.dashboard_window.resizable(False, False)
        self.dashboard_window.config(background=WIN_BACKGROUND)

        s = ttk.Style()
        s.configure('My.TFrame', background=WIN_BACKGROUND)
        s.configure('TLabel', background=WIN_BACKGROUND)
        s.configure('TLabelframe.Label', background=WIN_BACKGROUND)
        s.configure('TLabelframe', background=WIN_BACKGROUND)
        s.configure("Treeview.Heading", background='#DDDBCB')

        m_frame = ttk.Frame(self.dashboard_window, style='My.TFrame')
        m_frame.pack()

        self.menubar = Menu(self.dashboard_window, relief="raised", background='#4d4d4d', foreground='White')
        self.action_menubar = Menu(self.menubar, tearoff=0, background='#4d4d4d', foreground='White')
        self.menubar.add_cascade(label='Actions', menu=self.action_menubar)

        self.action_menubar.add_command(label='Add New', command=self.add_new)
        self.action_menubar.add_command(label='Edit', command=self.edit_record, state='disabled')
        self.action_menubar.add_command(label='Delete', command=self.delete_record, state='disabled')

        self.menubar.add_command(label='Copy URL', state='disabled', command=lambda: self.copy_data(1))
        self.menubar.add_command(label='Copy Username', state='disabled', command=lambda: self.copy_data(2))
        self.menubar.add_command(label='Copy Password', state='disabled', command=self.copy_password)

        self.dashboard_window.config(menu=self.menubar)

        search_lbl_frame = ttk.LabelFrame(m_frame, text='Search', relief='groove')
        search_lbl_frame.grid(row=0, column=0, sticky='ew', pady=10)

        title_label = ttk.Label(search_lbl_frame, text='Title')
        self.title_entry = ttk.Entry(search_lbl_frame)
        title_label.grid(row=0, column=0)
        self.title_entry.grid(row=0, column=1)

        self.featured_check_value = BooleanVar(value=False)
        featured_check = Checkbutton(
            search_lbl_frame, text='Show only featured records', variable=self.featured_check_value,
            onvalue=True, offvalue=False, command=self.filter_featured, background=WIN_BACKGROUND
        )
        featured_check.grid(row=0, column=2)

        self.show_pass_value = BooleanVar(value=False)
        show_pass_check = Checkbutton(
            search_lbl_frame, text='Show Password', variable=self.show_pass_value,
            onvalue=True, offvalue=False, command=self.show_password, background=WIN_BACKGROUND
        )
        show_pass_check.grid(row=0, column=3)

        for item in search_lbl_frame.winfo_children():
            item.grid_configure(padx=10, pady=7)

        self.title_entry.bind('<KeyRelease>', self.search_title)

        fields = ['Title', 'Login URL', 'Username', 'Password']

        self.data_treeview = ttk.Treeview(
            m_frame, columns=fields, show='headings', selectmode='browse', height=12
        )
        self.data_treeview.grid(row=2, column=0)

        for field in fields:
            self.data_treeview.heading(field, text=field)

        self.data_treeview.bind('<<TreeviewSelect>>', self.item_selected)
        self.data_treeview.bind('<ButtonRelease-3>', self.select_item)

        self.password_data = []

        self.fetch_data()

        self.dashboard_window.mainloop()

    def remove_all_rows(self):
        for child in self.data_treeview.get_children():
            self.data_treeview.delete(child)

    def reload_data(self):
        self.remove_all_rows()

        for row in self.password_data:
            self.add_item_in_treeview(
                uid=row[0], title=row[1], login_url=row[2], username=row[3], password=row[4], is_featured=row[5]
            )

    def show_password(self):
        self.reload_data()

    def search_title(self, event):
        self.reload_data()

        # for child in self.data_treeview.get_children():
        #     item = self.data_treeview.item(child)
        #     if self.title_entry.get().lower() not in item['values'][0].lower():
        #         self.data_treeview.delete(child)

    def filter_featured(self):
        self.reload_data()

    def add_item_in_treeview(self, uid, title, login_url, username, password, is_featured):
        if self.show_pass_value.get():
            pass_value = decrypt(password)
        else:
            pass_value = PASS_MASK_KEY

        if self.featured_check_value.get() is True and is_featured == 0:
            return

        if self.title_entry.get().lower() not in title:
            return

        self.data_treeview.insert(
            '', END, iid=uid, values=(title, login_url, username, pass_value),
            text=uid, tags=[username, decrypt(password), is_featured]
        )

    def add_record(self, uid, title, login_url, username, password, is_featured):
        self.add_item_in_treeview(uid, title, login_url, username, password, is_featured)
        self.password_data.append((uid, title, login_url, username, password, is_featured))

    def fetch_data(self):
        self.remove_all_rows()
        self.password_data = []

        connection = sqlite3.connect('passman.db')
        cursor = connection.cursor()

        sql_query = "select id, title, login_url, username, password, is_features from password_records;"

        cursor.execute(sql_query)
        for row in cursor.fetchall():
            uid = row[0]
            title = row[1]
            login_url = row[2]
            username = row[3]
            password = row[4]
            is_featured = row[5]

            self.add_record(
                uid=uid, title=title, login_url=login_url,
                username=username, password=password, is_featured=is_featured
            )

        connection.commit()
        connection.close()

    def select_item(self, event):
        cur_item = self.data_treeview.focus()
        col = self.data_treeview.identify_column(event.x)
        print('col = ', col)
        selected_row = self.data_treeview.item(cur_item)

        print(selected_row)

        if col == '#2':
            print(selected_row['values'][1])

        if col == '#3':
            print(selected_row['values'][2])

    def enable_disable_edit_delete(self, state):
        for action in ('Edit', 'Delete'):
            self.action_menubar.entryconfig(action, state=state)

    def item_selected(self, event):
        state = 'normal' if len(self.data_treeview.selection()) > 0 else 'disabled'
        self.enable_disable_edit_delete(state=state)

        for item in ('Copy URL', 'Copy Username', 'Copy Password'):
            self.menubar.entryconfig(item, state=state)

    def add_new(self):
        RecordEntry(self.dashboard_window, self.fetch_data)

    def edit_record(self):
        selected_item = self.data_treeview.selection()[0]
        item = self.data_treeview.item(selected_item)
        RecordEntry(self.dashboard_window, self.fetch_data, item['text'])

    def delete_record(self):
        msg_result = messagebox.askyesno(
            'Delete conformation', 'Are you sure to delete this record?'
        )

        if msg_result is False:
            return

        conn = sqlite3.connect('passman.db')
        cursor = conn.cursor()

        for selected_item in self.data_treeview.selection():
            item = self.data_treeview.item(selected_item)
            cursor.execute('delete from password_records where id=?', (item['text'],))

        conn.commit()
        conn.close()

        self.fetch_data()

    def copy_data(self, index_no):
        selected_item = self.data_treeview.selection()[0]
        item = self.data_treeview.item(selected_item)
        clipboard.copy(item['values'][index_no])

    def copy_password(self):
        selected_item = self.data_treeview.selection()[0]
        item = self.data_treeview.item(selected_item)
        clipboard.copy(item['tags'][1])

# Dashboard()
