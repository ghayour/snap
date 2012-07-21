# -*- coding: utf-8 -*-
__docformat__ = 'reStructuredText'
from datetime import date
from string import split
import datetime

from arsh.shamsi.date.calverter import Calverter


MONTHS = (
"فروردين", "ارديبهشت", "خرداد", "تير", "مرداد", "شهريور", "مهر", "آبان", "آذر", "دي", "بهمن", "اسفند")

def get_jalali(value):
    """
    :type value:datetime.date

    :rtype: jalali:tuple
    :return:jalali
    """
    cal = Calverter()
    jd = cal.gregorian_to_jd(value.year, value.month, value.day)
    jalali = cal.jd_to_jalali(jd)
    return jalali


def expand_month_day(value):
    if len(str(value)) == 1:
        result = "0%s" % value
        return result
    return value

def split_date(str):
    """
    split date string with "-" and return tuple with three integer number year, month, day

    :type str:str
    """
    l1 = split(str, "-")
    year = int(l1[0])
    month = int(l1[1])
    day = int(l1[2])
    return year, month, day


def convert_stringdate_to_pythondate(str):
    """
    convert string date like "2012-1-1" to python datetime.date

    :type str:str
    :rtype datetime.date
    """
    l1 = split(str, "-")
    year = int(l1[0])
    month = int(l1[1])
    day = int(l1[2])
    return date(year, month, day)


def pdate_string(value, forceTime=False):
    """
    get miladi date and return persian date in string format.
    example: if n=datetime.datetime(2012, 6, 24, 15, 48, 24, 138000)
             pdate_string(n) return '1391-04-04'
             pdate_string(n,True) return '1391/4/4 15:48:24'

    :type value: datetime.datetime
    :type forceTime:bool
    :param forceTime: present time or no
    :rtype: str
    """
    jalali = get_jalali(value.date())
    if forceTime:
        try:
            h = value.hour
            m = value.minute
            s = value.second
            return "%s/%s/%s %s:%s:%s" % (jalali[0], jalali[1], jalali[2], h, m, s)
        except:
            pass

    return str(jalali[0]) + "-" + expand_month_day(str(jalali[1])) + "-" + expand_month_day(str(jalali[2]))


def pdate(value):
    """
    get a miladi date and return persian datetime.date
     example: datetime.date(1391, 4, 4)

    :type value:datetime.date
    :rtype datetime.date
    """
    cal = Calverter()
    jd = cal.gregorian_to_jd(value.year, value.month, value.day)
    y, m, d = cal.jd_to_jalali(jd)
    return date(year=y, month=m, day=d)


def pdate_separated(value):
    """
    get a miladi date and return a tuple with three number in persian date.
    example: pdate_seperate(datetime.date(2012, 6, 24)) return (1391, 4, 4)

    :type value: datetime.date
    :rtype: tuple(int,int,int)
    """
    cal = Calverter()
    jd = cal.gregorian_to_jd(value.year, value.month, value.day)
    y, m, d = cal.jd_to_jalali(jd)
    return y, m, d


def pdate_slash(value):
    """
    return persian date in string format seperated with '/' .
    example: '1391/4/4'

    :type value: datetime.date
    :rtype: str
    """
    jalali = get_jalali(value)
    return str(jalali[0]) + "/" + str(jalali[1]) + "/" + str(jalali[2])


def pdate_persian_month(value):
    """
    return persian date in string format.
    example: 1 تير 1391

    :type value: datetime.date
    :rtype: str
    """
    jalali = get_jalali(value)
    return str(jalali[2]) + " " + MONTHS[jalali[1] - 1] + " " + str(jalali[0])


def pdate_persian_month_weekday(value):
    """
    return persian date in format unicode.
    example: پنجشنبه 1 تير 1391

    :type value:datetime.date
    :rtype:unicode
    """
    cal = Calverter()
    jd = cal.gregorian_to_jd(value.year, value.month, value.day)
    jalali = cal.jd_to_jalali(jd)
    return cal.JALALI_WEEKDAYS[cal.jwday(jd)] + "، " + str(jalali[2]) + " " + MONTHS[jalali[1] - 1] + " " + str(
        jalali[0])


def pdate_time(value):
    """
    get a miladi datetime and return persian datetime
    example: pdate_time(datetime.datetime.now()) return datetime.datetime(1391, 4, 4, 15, 20, 27)

    :type value: datetime.datetime
    :rtype: datetime.datetime
    """
    cal = Calverter()
    jd = cal.gregorian_to_jd(value.year, value.month, value.day)
    y, m, d = cal.jd_to_jalali(jd)
    return datetime.datetime(year=y, month=m, day=d, hour=value.hour, minute=value.minute, second=value.second)

def pdate_time_persian_month(value):
    """
    return persian datetime in format string.
    example: '4 تير 1391 14:5:14'
    :type value:datetime.datetime
    :rtype str
    """
    jalali = get_jalali(value)
    return str(jalali[2]) + " " + MONTHS[jalali[1] - 1] + " " + str(jalali[0]) + " " + "%d:%d:%d" % (
        value.hour, value.minute, value.second)

def pdate_to_miladi(value):
    """
    convert persian date to miladi date
    example: datetime.date(1391, 4, 4) convert to datetime.date(2012, 6, 24)

    :type value:datetime.date
    :rtype:datetime.datejaladjalddawe
    """
    cal = Calverter()
    jd = cal.jalali_to_jd(value.year, value.month, value.day)
    y, m, d = cal.jd_to_gregorian(jd)
    return date(year=y, month=m, day=d)


def pdate_separate_to_miladi(year, month, day):
    """
    get three integer number of persian date and return miladi datetime.date
    example: pdate_separate_to_miladi(1391,4,4) return datetime.date(2012, 6, 24)

    :type year:int
    :type month:int
    :type day:int
    :rtype date:datetime.date
    """
    cal = Calverter()
    jd = cal.jalali_to_jd(year, month, day)
    y, m, d = cal.jd_to_gregorian(jd)
    return date(year=y, month=m, day=d)


def format_relative_date(d):
    #TODO: convert to farsi date
    #TODO: rewrite with more care
    now = datetime.datetime.utcnow()
    diff = now - d
    year = d.strftime('%y')
    diff_min = int(((float(diff.seconds) + float(diff.microseconds) / 1000000.0) / 60.0) % 60)
    diff_hour = int((float(diff.seconds)/3600) % 24)
    diff_month =int(diff.days)/31
    a = 'time'
    if year == now.strftime('%y'):
        if abs(int(diff.days)) < 31:
            if abs(int(diff.days)) < 1:
                if diff_hour > 1:
                    a = str(diff_hour)+ u" ساعت قبل"
                else:
                    if diff.seconds < 60:
                        a = u'چند لحظه قبل'
                    elif diff_min < 60 :
                        a =  str(diff_min) + u" دقیقه قبل "
            elif abs(int(diff.days)) == 1:
                a = u"دیروز"
            else:
                a = str(abs(int(diff.days))) + u" روز پیش"
        else:
            a = str(diff_month)+u" ماه پیش"
    else:
        a = str(int(now.strftime('%y')) - int(year))+u" سال پیش"
    return a
