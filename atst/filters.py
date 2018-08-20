import re

def iconSvg(name):
    with open('static/icons/'+name+'.svg') as contents:
        return contents.read()


def dollars(value):
    try:
        numberValue = float(value)
    except ValueError:
        numberValue = 0
    return "${:,.0f}".format(numberValue)


def usPhone(number):
    phone = re.sub(r'\D', '', number)
    return '+1 ({}) {} - {}'.format(phone[0:3], phone[3:6], phone[6:])


def readableInteger(value):
    try:
        numberValue = int(value)
    except ValueError:
        numberValue = 0
    return "{:,}".format(numberValue)


def register_filters(app):
    app.jinja_env.filters['iconSvg'] = iconSvg
    app.jinja_env.filters['dollars'] = dollars
    app.jinja_env.filters['usPhone'] = usPhone
    app.jinja_env.filters['readableInteger'] = readableInteger

