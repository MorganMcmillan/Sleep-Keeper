import tkinter as tk
import sqlite3 as sql
from datetime import date
from calendar_widget import make_calendar

BACKGROUND = "orange2"

def get_month_sleep_info(cur: sql.Cursor, today):
    cur.execute(f"SELECT * FROM sleep WHERE date LIKE '{today.year}-%{today.month}-%';")
    rows = cur.fetchall()
    month_sleep_info = { date.fromisoformat(row[0]).day: row[1:3] for row in rows}
    return month_sleep_info

def main():
    # Init window
    global root
    root = tk.Tk()
    root.title("Sleep Keeper")
    root.geometry("500x500")
    root.config(bg=BACKGROUND)
    
    # Init DB
    con = sql.connect("sleep.db")
    cur = con.cursor()

    # `date` stored in the format of YYYY-MM-DD
    # `slept_at` is stored as HH:MM A.M.|P.M.
    cur.execute("CREATE TABLE IF NOT EXISTS sleep(date TEXT PRIMARY KEY, slept_at TEXT, hours_slept FLOAT);")

    # Get this month's info
    today = date.today()
    month_sleep_info = get_month_sleep_info(cur, today)

    # Create calendar with today's date
    calendar = make_calendar(root, today, month_sleep_info, 8, con, cur)
    calendar.pack(anchor="n")

    root.mainloop()
    # Cleanup logic
    con.commit()
    cur.close()
    con.close()

if __name__ == "__main__":
    main()