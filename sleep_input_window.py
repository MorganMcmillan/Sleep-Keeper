import tkinter as tk
from tkinter import messagebox
import sqlite3 as sql
from datetime import date

def day_clicked(button: tk.Button, current_date: date, root: tk.Tk, con: sql.Connection, cur: sql.Cursor):
    today = date.today()
    if current_date > today:
        messagebox.showwarning("Future Date Selected", f"You cannot enter your sleep information for a date that's in the future. (Today's date is {today})")
        return

    # TODO: show today's information if the user already entered it
    sub = tk.Toplevel(root)
    sub.geometry("500x500")
    
    # Get today's sleep info, if any
    cur.execute("SELECT slept_at, hours_slept FROM sleep WHERE date = ?;", (str(current_date),))
    sleep_info = cur.fetchone()

    def update_sleep_info(slept_at, hours_slept):
        delete_children(info_frame)
        tk.Label(info_frame, text=f"Hours of sleep today: {hours_slept}").pack(anchor="n")
        tk.Label(info_frame, text=f"Went to sleep at: {slept_at}").pack(anchor="n")

    tk.Label(sub, text=f"Date: {current_date}").pack(anchor="n")
    info_frame = tk.Frame(sub)
    if sleep_info:
        update_sleep_info(sleep_info[0], sleep_info[1])
    info_frame.pack(anchor="n")


    sleep_frame = tk.Frame(sub)
    tk.Label(sleep_frame, text="Enter the time you fell asleep at (Ex: 11:00)").grid(row=0, column=0)
    var_slept_at = tk.StringVar()
    tk.Entry(sleep_frame, textvariable=var_slept_at).grid(row=0, column=1)
    # Use option list for "A.M" or "P.M" to prevent inconsistent formatting
    am_pm = tk.Variable(value=["A.M.", "P.M."])
    listbox = tk.Listbox(sleep_frame, selectmode="single", listvariable=am_pm, height=2, width=4)
    listbox.grid(row=0, column=2)
    sleep_frame.pack(anchor="n")

    hours_frame = tk.Frame(sub)
    tk.Label(hours_frame, text="Enter hours slept").grid(row=0, column=0)
    var_hours_slept = tk.StringVar()
    tk.Entry(hours_frame, textvariable=var_hours_slept).grid(row=0, column=1)
    hours_frame.pack(anchor="n")

    def update_todays_color(button, hours, needed):
        (bg, fg) = get_sleep_color(hours, needed)
        fg = "deep sky blue" if current_date == today else fg
        button.config(bg=bg, fg=fg)

    def record_sleep_info():
        try:
            time_slept_at = var_slept_at.get() + " " + am_pm.get()[listbox.curselection()[0]]
        except IndexError:
            if len(var_slept_at.get()) == 0:
                time_slept_at = "12:00 A.M."
            else:
                time_slept_at = var_slept_at.get() + " P.M."

        time_slept_at = validate_time(time_slept_at)
        hours_slept = validate_hour(var_hours_slept.get())
        
        try: # to actually insert/replace today's sleep information
            cur.execute("INSERT OR REPLACE INTO sleep (date, hours_slept, slept_at) VALUES (?, ?, ?);", (str(current_date), hours_slept, time_slept_at))
            con.commit()
            update_todays_color(button, hours_slept, 8)
            update_sleep_info(time_slept_at, hours_slept)
            root.event_generate("<<today's_info_recorded>>", when="tail")
        except sql.IntegrityError as err:
            messagebox.showerror("Integrity error!", err)
        except InvalidTimeError as err:
            messagebox.showerror("Invalid time entered!", err)
        except Exception as err:
            messagebox.showerror("Error!", err)

    def delete_sleep_info():
        cur.execute("DELETE FROM sleep WHERE date = ?;", (str(current_date),))
        con.commit()
        update_todays_color(button, None, 8)
        delete_children(info_frame)
        root.event_generate("<<today's_info_deleted>>", when="tail")

    button_group = tk.Frame(sub)
    record_btn = tk.Button(button_group, text="Record", command=record_sleep_info)
    record_btn.pack(side="left")
    delete_btn = tk.Button(button_group, text="Delete", command=delete_sleep_info)
    delete_btn.pack(side="left", padx=16)
    button_group.pack(anchor="n")


def get_sleep_color(hours_slept: float, hours_of_sleep_needed: float):
    if hours_slept is None:
        return ("grey", "black")
    elif hours_slept == 0:
        return ("black", "white")
    elif hours_slept == 24:
        return ("white", "black")

    delta_slept = hours_slept - hours_of_sleep_needed
    if delta_slept <= -3.0:
        return ("VioletRed4", "black")
    elif delta_slept <= -2.0:
        return ("red2", "black")
    elif delta_slept <= -1.0:
        return ("orange", "black")
    elif delta_slept < 0.0:
        return ("gold2", "black")
    elif delta_slept < 2.0:
        return ("green2", "black")
    else:
        return ("blue2", "white")
    
def delete_children(widget):
    children = [v for v in widget.children.values()]
    for child in children:
        child.destroy()

class InvalidTimeError(Exception):
    def __init__(self, malformed_hour):
        message = f"Invalid hour entered. Hours should contain only numbers, and be within the range of 1:00 to 12:59. (Got: {malformed_hour})"
        super().__init__(message)

# Checks hour format
def validate_time(time: str):
    import re
    hour_match = re.search("^1?\\d:[0-5]\\d", time)
    if hour_match is None:
        raise InvalidTimeError(time)
    
    am_pm_match = re.search("[A|P]\\.M\\.", time)
    if am_pm_match is None:
        raise InvalidTimeError(time)
    return hour_match.group(0) + " " + am_pm_match.group(0)

def validate_hour(hour: str):
    import re
    try: # to parse hour as a decimal
        return float(hour)
    except: # Maybe it's in the format of "hh:mm"?
        hour_match = re.match("(\\d{1,2}):([0-5]\\d)", hour)
        if hour_match is None:
            raise InvalidTimeError(hour)
        return int(hour_match.group(1)) + int(hour_match.group(2)) / 60