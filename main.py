import tkinter as tk
import sqlite3 as sql
from datetime import date
from calendar_widget import Calendar
from functools import partial

from parse import parse_hour
from sleep_input_window import day_clicked
from sleep_stats_window import sleep_stats_clicked, running_sleep_debt

# IDEAS:
# - Import/export to/from CSV
# - Add arrow buttons for viewing previous months

BACKGROUND = "orange2"
# TODO: Set this to false for release versions
DEBUG = True

def dbg_time_slept_parsed(cur: sql.Cursor):
    cur.execute("SELECT slept_at FROM sleep;")
    slept_ats = cur.fetchall()
    slept_ats = list(map(lambda s: parse_hour(s[0]), slept_ats))
    print("unmassaged:", slept_ats)
    for i in range(len(slept_ats)):
        if slept_ats[i] <= 6:
            slept_ats[i] = slept_ats[i] + 12
    print("avg:", sum(slept_ats) / len(slept_ats))
    return slept_ats

def icon(name: str):
    return tk.PhotoImage(file=f"icons/{name}.png")

def get_month_sleep_info(cur: sql.Cursor, today):
    cur.execute(f"SELECT * FROM sleep WHERE date LIKE '{today.year}-{today.month:02d}-%';")
    rows = cur.fetchall()
    month_sleep_info = { date.fromisoformat(row[0]).day: row[1:3] for row in rows }
    return month_sleep_info

def init_db(cur):
    # `date` is stored in the format of YYYY-MM-DD
    # `slept_at` is stored as HH:MM A.M.|P.M.
    cur.execute("""CREATE TABLE IF NOT EXISTS sleep (
        date TEXT PRIMARY KEY,
        hours_slept FLOAT,
        slept_at TEXT,
        CONSTRAINT valid_hour_format CHECK (slept_at LIKE '%_:__ _.M.'),
        CONSTRAINT hours_slept_within_range CHECK (hours_slept BETWEEN 0 and 24)
    );""")

    cur.execute("""CREATE TABLE IF NOT EXISTS sleep_debt_paid (
        date TEXT PRIMARY KEY REFERENCES sleep (date)
    );""")

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

    init_db(cur)

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

    img_bed = icon("bed")
    btn_sleep_stats = tk.Button(sidebar, width=32, height=32, image=img_bed, command=partial(sleep_stats_clicked, root, con, cur))
    btn_sleep_stats.pack(anchor="n")

    # TODO: add a button that allows the user to enter their sleep goals
    img_medal = icon("medal")
    btn_sleep_goals = tk.Button(sidebar, width=32, height=32, image=img_medal)
    btn_sleep_goals.pack(anchor="n")

    # Bind events
    root.bind("<<today's_info_deleted>>", lambda _: add_today_button())
    root.bind("<<today's_info_recorded>>", lambda _: remove_today_button())
    
    if DEBUG:
        # Bind debug keys
        root.bind("a", lambda _: print(running_sleep_debt(cur)))
        root.bind("s", lambda _: print(root.winfo_width(), root.winfo_height()))
        root.bind("d", lambda _: print(dbg_time_slept_parsed(cur)))

    root.mainloop()

    # Cleanup logic
    con.commit()
    cur.close()
    con.close()

if __name__ == "__main__":
    main()
