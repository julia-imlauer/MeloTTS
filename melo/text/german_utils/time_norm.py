import re
import inflect

_inflect = inflect.engine()

_time_re = re.compile(
    r"""\b
                          ((0?[0-9])|(1[0-9])|(2[0-3]))  # hours
                          :
                          ([0-5][0-9])                  # minutes
                          \b""",
    re.IGNORECASE | re.X,
)

def _expand_num(n: int) -> str:
    return _inflect.number_to_words(n, lang='de')

def _expand_time_german(match: "re.Match") -> str:
    hour = int(match.group(1))
    minute = int(match.group(5))
    time = []

    # Handling full hour without minutes
    if minute == 0:
        time.append(f"{_expand_num(hour)} Uhr")
    else:
        # Handling special expressions for "halb", "viertel", etc.
        if minute == 15:
            time.append(f"Viertel nach {_expand_num(hour)}")
        elif minute == 30:
            time.append(f"halb {_expand_num(hour + 1)}")
        elif minute == 45:
            time.append(f"Viertel vor {_expand_num(hour + 1)}")
        else:
            # General case: "hour Uhr minute"
            time.append(f"{_expand_num(hour)} Uhr {_expand_num(minute)}")

    # Handle 24-hour conversion for afternoon/evening
    if hour < 12:
        time.append("vormittags")
    elif hour < 18:
        time.append("nachmittags")
    else:
        time.append("abends")

    return " ".join(time)

def expand_time_german(text: str) -> str:
    return re.sub(_time_re, _expand_time_german, text)
