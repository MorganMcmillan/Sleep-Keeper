import tkinter as tk
from tkinter import messagebox
import sqlite3 as sql
from datetime import date

# TODO: display the following:
# Date of best sleep time

def sleep_stats_clicked(root: tk.Tk, con: sql.Connection, cur: sql.Cursor):
    sub = tk.Toplevel(root)
    sub.geometry("500x500")

    cur.execute("SELECT COUNT(*) FROM sleep;")
    days_entered = cur.fetchone()[0]

    cur.execute("SELECT AVG(hours_slept) FROM sleep;")
    avg_hours_slept = cur.fetchone()[0]

    avg_time_of_sleep = get_avg_time_of_sleep(cur)

    current_sleep_debt = running_sleep_debt(cur)[-1]

    cur.execute("SELECT MAX(hours_slept) FROM sleep;")
    most_hours_slept = cur.fetchone()[0]

    cur.execute("SELECT date FROM sleep WHERE hours_slept = ? ORDER BY date LIMIT 1;", (most_hours_slept,))
    best_sleep_date = cur.fetchone()[0]

    # Display info

    tk.Label(sub, text=f"Number of days entered: {days_entered}").pack(anchor="n")
    tk.Label(sub, text=f"Average number of hours slept: {avg_hours_slept}").pack(anchor="n")
    tk.Label(sub, text=f"Average time of sleep: {"todo"}").pack(anchor="n")
    tk.Label(sub, text=f"Current sleep debt: {current_sleep_debt}").pack(anchor="n")
    tk.Label(sub, text=f"Best sleep was on {best_sleep_date}").pack(anchor="n")
    tk.Label(sub, text=f"Best length of sleep: {most_hours_slept} hours").pack(anchor="n")

# TODO: parse each time into a numerical format that can be averaged
def get_avg_time_of_sleep(cur: sql.Cursor):
    pass

def running_sleep_debt(cur: sql.Cursor):
    from itertools import accumulate
    debts = cur.execute("SELECT 8 - hours_slept FROM sleep ORDER BY date;").fetchall()
    # We can never have negative sleep debt
    return list(accumulate(map(lambda x: x[0], debts), lambda acc, x: max(acc + x, 0)))

def sleep_debts_paid(cur: sql.Cursor):
    dates = cur.execute("SELECT date FROM sleep ORDER BY date;").fetchall()
    debts = running_sleep_debt(cur)
    return [dates[i][0] for i in range(len(dates)) if debts[i] == 0]