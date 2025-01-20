import tkinter as tk
import sqlite3 as sql
from datetime import date
from calendar_widget import Calendar
from functools import partial

from sleep_input_window import day_clicked

BACKGROUND = "orange2"
# TODO: Set this to false for release versions
DEBUG = True

def icon(name: str):
    return tk.PhotoImage(file=f"icons/{name}.png")

def get_month_sleep_info(cur: sql.Cursor, today):
    cur.execute(f"SELECT * FROM sleep WHERE date LIKE '{today.year}-%{today.month}-%';")
    rows = cur.fetchall()
    month_sleep_info = { date.fromisoformat(row[0]).day: row[1:3] for row in rows}
    return month_sleep_info

def running_sleep_debt(cur: sql.Cursor):
    from itertools import accumulate
    debts = cur.execute("SELECT date, 8 - hours_slept FROM sleep ORDER BY date;").fetchall()
    print(debts)
    accumulated_sleep_debts = list(accumulate(map(lambda x: x[1] ,debts)))
    print(accumulated_sleep_debts)


def main():
    # Init window
    root = tk.Tk()
    root.title("Sleep Keeper")
    root.geometry("216x200")
    root.config(bg=BACKGROUND)
    root.minsize(344, 0)
    
    # Init DB
    # TODO: store this in an OS appropriate place, like appdata
    con = sql.connect("sleep.db")
    cur = con.cursor()

    # `date` stored in the format of YYYY-MM-DD
    # `slept_at` is stored as HH:MM A.M.|P.M.

    cur.execute("""CREATE TABLE IF NOT EXISTS sleep (
        date TEXT PRIMARY KEY,
        hours_slept FLOAT,
        slept_at TEXT,
        sleep_debt_paid BOOLEAN DEFAULT FALSE,
        CONSTRAINT valid_hour_format CHECK (slept_at LIKE '%_:__ _.M.'),
        CONSTRAINT hours_slept_within_range CHECK (hours_slept BETWEEN 0 and 24)
    );""")

    # Get this month's info
    today = date.today()
    month_sleep_info = get_month_sleep_info(cur, today)

    # Create calendar with today's date
    calendar = Calendar(root, BACKGROUND, today, month_sleep_info, 8, con, cur)
    calendar.frame.pack(anchor="n")

    # Pester the user to enter their sleep information if they haven't today
    def add_today_button():
        if add_today_button.shown: # Prevent button from being added twice
            return
        global enter_today_btn
        enter_today_btn = tk.Button(root, text="Enter today's sleep info!", command=partial(day_clicked, calendar.days[today.day - 1], today, root, con, cur))
        enter_today_btn.pack(anchor="n", pady=8)
        add_today_button.shown = True
    # Cursed method to implement static variables in python
    add_today_button.shown = False

    def remove_today_button():
        enter_today_btn.destroy()
        add_today_button.shown = False

    # Check if sleep info exists from today
    cur.execute("SELECT date FROM sleep WHERE date = ?;", (str(today),))
    if cur.fetchone() is None:
        add_today_button()

    # Add sidebar for misc widgets
    sidebar = tk.Frame(root, bg="yellow", width=48, height=4096)
    sidebar.place(x=0, y=0)
    sidebar.pack_propagate(False)

    # TODO: add a window that displays the overall stats of the user's sleep (sleep debt, average bedtime, average wakeup time, Etc.)
    img_bed = icon("bed")
    btn_sleep_stats = tk.Button(sidebar, width=32, height=32, image=img_bed)
    btn_sleep_stats.pack(anchor="n")

    # Bind events
    root.bind("<<today's_info_deleted>>", lambda _: add_today_button())
    root.bind("<<today's_info_recorded>>", lambda _: remove_today_button())
    
    if DEBUG:
        # Bind debug keys
        root.bind("a", lambda _: running_sleep_debt(cur))
        root.bind("s", lambda _: print(root.winfo_width(), root.winfo_height()))

    root.mainloop()

    # Cleanup logic
    con.commit()
    cur.close()
    con.close()

if __name__ == "__main__":
    main()