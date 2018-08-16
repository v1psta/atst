import pendulum


def parse_date(data):
    date_formats = ["YYYY-MM-DD", "MM/DD/YYYY"]
    for _format in date_formats:
        try:
            return pendulum.from_format(data, _format).date()
        except (ValueError, pendulum.parsing.exceptions.ParserError):
            pass

    raise ValueError("Unable to parse string {}".format(data))
