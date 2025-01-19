import tkinter as tk
from datetime import date
from functools import partial
from sleep_input_window import day_clicked, get_sleep_color

class Calendar:
    def __init__(self, root, bg, todays_date: date, month_sleep_info, hours_of_sleep_needed, con, cur):
        self.frame = tk.Frame(bg=bg)
        self.days = [None] * 31
        # Offsets the first calendar day by what day of the week it is
        day_offset = date(todays_date.year, todays_date.month, 1).isoweekday()

        # Create day for each month
        for i in range(1, get_days_in_month(todays_date.month, todays_date.year) + 1):
            day_sleep_info = month_sleep_info.get(i)
            (bg, fg) = get_sleep_color(day_sleep_info and day_sleep_info[0], hours_of_sleep_needed)
            this_date = date(todays_date.year, todays_date.month, i)

            day = tk.Button(self.frame, text=i, width=3, fg=fg, bg=bg)
            # `partial` is used to bind variables to function arguments for later use
            # This means that when this day is clicked, this function will be called with the exact same arguments
            day.config(command=partial(day_clicked, day, this_date, root, con, cur))
            # Highlight today
            if i == todays_date.day:
                day.config(fg="deep sky blue")
            day.grid(column=(i - 1 + day_offset)%7, row=(i - 1 + day_offset)//7)
            self.days[i - 1] = day

DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def get_days_in_month(month: int, year: int):
    if month == 2 and year % 4 == 0:
        return 29
    return DAYS_IN_MONTH[month - 1]
