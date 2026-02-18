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
    
    am_pm_match = re.search("[AP]\\.M\\.", time)
    if am_pm_match is None:
        raise InvalidTimeError(time)
    return hour_match.group(0) + " " + am_pm_match.group(0)

def validate_hour(hour: str):
    import re
    try: # to parse hour as a decimal
        return float(hour)
    except Exception as _: # Maybe it's in the format of "hh:mm"?
        hour_match = re.match("(\\d{1,2}):([0-5]\\d)", hour)
        if hour_match is None:
            raise InvalidTimeError(hour)
        return int(hour_match.group(1)) + int(hour_match.group(2)) / 60
