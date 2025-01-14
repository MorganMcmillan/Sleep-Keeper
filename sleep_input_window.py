import tkinter as tk
from tkinter import messagebox
import sqlite3 as sql
from datetime import date

def day_clicked(button: tk.Button, current_date: date, root: tk.Tk, con: sql.Connection, cur: sql.Cursor):
    today = date.today()
    if current_date > today:
        messagebox.showwarning("Future Date Selected", f"You cannot enter your sleep information for a date that's in the future. (Today's date is {today})")
        return

    # TODO: when a day is clicked, open a new window to ask the user for their sleep information
    # The information will then be recorded in the SQL database
    # If the day is after today, then the user will be prevented from entering information
    sub = tk.Toplevel(root)
    sub.geometry("500x500")

    tk.Label(sub, text=f"Date: {current_date}").pack(anchor="nw")

    sleep_frame = tk.Frame(sub)
    tk.Label(sleep_frame, text="Enter the time you fell asleep at (Ex: 11:00)").grid(row=0, column=0)
    slept_at = tk.StringVar()
    tk.Entry(sleep_frame, textvariable=slept_at).grid(row=0, column=1)
    # Use option list for "A.M" or "P.M" to prevent inconsistent formatting
    am_pm = tk.Variable(value=["A.M.", "P.M."])
    listbox = tk.Listbox(sleep_frame, selectmode="single", listvariable=am_pm, height=2, width=4)
    listbox.grid(row=0, column=2)
    sleep_frame.pack(anchor="nw")

    hours_frame = tk.Frame(sub)
    tk.Label(hours_frame, text="Enter hours slept").grid(row=0, column=0)
    hours_slept = tk.DoubleVar()
    tk.Entry(hours_frame, textvariable=hours_slept).grid(row=0, column=1)
    hours_frame.pack(anchor="nw")

    def update_todays_color(button, hours, needed):
        (bg, fg) = get_sleep_color(hours, needed)
        fg = "deep sky blue" if current_date == today else fg
        button.config(bg=bg, fg=fg)

    def record_sleep_info():
        try:
            time_slept_at = slept_at.get() + am_pm.get()[listbox.curselection()[0]]
        except IndexError:
            time_slept_at = "12:00 A.M."
        
        cur.execute("INSERT OR REPLACE INTO sleep VALUES (?, ?, ?)", (str(current_date), time_slept_at, hours_slept.get()))
        con.commit()

        update_todays_color(button, hours_slept.get(), 8)

    def delete_sleep_info():
        cur.execute("DELETE FROM sleep WHERE date = ?", (str(current_date),))
        con.commit()
        update_todays_color(button, None, 8)

    button_group = tk.Frame(sub)
    record_btn = tk.Button(button_group, text="Record", command=record_sleep_info)
    record_btn.grid(row=0, column=0)
    delete_btn = tk.Button(button_group, text="Delete", command=delete_sleep_info)
    delete_btn.grid(row=0, column=1)
    button_group.pack(anchor="nw")


def get_sleep_color(hours_slept, hours_of_sleep_needed):
    if hours_slept is None:
        return ("grey", "black")
    elif hours_slept == 0:
        return ("black", "white")
    elif hours_slept == 24:
        return ("white", "black")

    delta_slept = hours_slept - hours_of_sleep_needed
    if delta_slept <= -2.0:
        return ("red2", "black")
    elif delta_slept <= -1.0:
        return ("orange", "black")
    elif delta_slept < 0.0:
        return ("gold2", "black")
    elif delta_slept < 2.0:
        return ("green2", "black")
    else:
        return ("blue2", "white")