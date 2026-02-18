from validation import InvalidTimeError

def parse_hour(hour: str):
    import re
    hour_match = re.match("(\\d{1,2}):([0-5]\\d) ([AP]M)", hour)
    if hour_match is None:
        raise InvalidTimeError(hour)
    time = int(hour_match.group(1))
    is_pm = hour_match.group(3) == "PM"
    if time == 12:
        time = 0
    if is_pm:
        time += 12
    return time + int(hour_match.group(2)) / 60

def unparse_time(hour: float):
    is_pm = hour >= 12
    if is_pm:
        hour -= 12
    if hour == 0:
        hour = 12
    return f"{int(hour)}:{int((hour - int(hour)) * 60):02d} {'PM' if is_pm else 'AM'}"