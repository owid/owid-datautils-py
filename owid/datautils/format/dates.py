from datetime import datetime, timedelta, date
from contextlib import contextmanager
import locale
import threading
from sys import platform
from typing import Union
import pytz
import re
import unicodedata

import pandas as pd
import epiweeks


LOCALE_LOCK = threading.Lock()
DEFAULT_LOCALE = "C"  # "en_US.ISO8859-1"
DATE_FORMAT = "%Y-%m-%d"


def week_to_date(year: int, week: int, output_fmt: str = DATE_FORMAT):
    week = epiweeks.Week(year, week)
    dt = week.enddate()
    return clean_date(dt, output_fmt=output_fmt)


def clean_date(
    date_or_text: Union[str, datetime, date],
    fmt: str = None,
    lang: str = "en",
    loc: str = "",
    minus_days: int = 0,
    unicode_norm: bool = True,
    output_fmt: str = DATE_FORMAT,
    as_datetime: bool = False,
):
    """Extract a date from a `text`.

    The date from text is extracted using locale `loc`. Alternatively, you can provide language `lang` instead.

    By default, system default locale is used.

    Args:
        date_or_text (Union[str, datetime, date]): Input text or date.
        fmt (str, optional): Text format. More details at
                             https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes.
        lang (str, optional): Language two-letter code, e.g. 'da' (dansk). If given, `loc` will be ignored and redefined
                                based on `lang`. Defaults to None.
        loc (str, optional): Locale, e.g es_ES. Get list of available locales with `locale.locale_alias` or
                                `locale.windows_locale` in windows. Defaults to "" (system default).
        minus_days (int, optional): Number of days to subtract. Defaults to 0.
        unicode_norm (bool, optional): [description]. Defaults to True.
        output_fmt (str, optional): Format of the output date. By default, uses `DATE_FORMAT`.
        as_datetime (bool, optional): Set to True to return the date as a datetime.

    Returns:
        str: Extracted date in format %Y-%m-%d
    """
    if isinstance(date_or_text, (datetime, date)):
        return date_or_text.strftime(output_fmt)
    # If lang is given, map language to a locale
    if fmt is None:
        raise ValueError("Input date format is required!")
    if loc == "" and lang is not None:
        if lang in locale.locale_alias:
            loc = locale.locale_alias[lang]
    if platform == "win32":
        if loc is not None:
            loc = loc.replace("_", "-")
    # Unicode
    if unicode_norm:
        date_or_text = text_new = unicodedata.normalize("NFKC", date_or_text).strip()
    # Fix possible issues
    date_or_text = (
        date_or_text.replace("O", "0").replace("0CT", "OCT").replace("0ct", "Oct")
    )
    # Thread-safe extract date
    with _setlocale(loc):
        dt = datetime.strptime(date_or_text, fmt) - timedelta(days=minus_days)
        if not as_datetime:
            return dt.strftime(output_fmt)
        return dt


def extract_clean_date(
    text: str,
    regex: str,
    date_format: str,
    lang: str = "en",
    loc: str = "",
    minus_days: int = 0,
    unicode_norm: bool = True,
    replace_year=None,
):
    """Export clean date from raw text using RegEx.

    ..  code-block:: python

        >>> from cowidev.utils import extract_clean_date
        >>> text = "Something irrelevant. This page was last updated on 25 May 2021 at 09:05hrs."
        >>> date_str = extract_clean_date(
            text=text,
            regex=r"This page was last updated on (\d{1,2} May 202\d) at \d{1,2}:\d{1,2}hrs",
            date_format="%d %B %Y",
            minus_days=1,
        )

    Args:
        text (str): Raw original text.
        regex (str): RegEx to export date fragment. Should have the data grouped (group number 1)
        date_format (str): Format of the date (was extracted using regex).
        lang (str, optional): Language two-letter code, e.g. 'da' (dansk). If given, `loc` will be ignored and redefined
                                based on `lang`. Defaults to None.
        loc (str, optional): Locale, e.g es_ES. Get list of available locales with `locale.locale_alias` or
                                `locale.windows_locale` in windows. Defaults to "" (system default).
        minus_days (int, optional): Number of days to subtract. Defaults to 0.
        unicode_norm (bool, optional): [description]. Defaults to True.
        replace_year (str): Replace the year with this one.
    """
    if unicode_norm:
        text = clean_string(text)
    date_raw = re.search(regex, text).groups()
    if isinstance(date_raw, tuple):
        date_raw = " ".join(date_raw)
    date_str = clean_date(
        date_raw,
        fmt=date_format,
        lang=lang,
        loc=loc,
        minus_days=minus_days,
        unicode_norm=unicode_norm,
    )
    if replace_year is not None:
        date_str = _replace_date_fields(date_str, {"year": replace_year})
    return date_str


def _replace_date_fields(
    date_raw: str, replace_fields: dict = {}, date_format: str = DATE_FORMAT
):
    """Replace date field.

    Args:
        date_raw (str): Date raw in standard format %Y-%m-%d.
        replace_fields (dict, optional): Fields to replace. Format should be: dict(field, value), e.g. {year: "2021"}.
        date_format (str, optional): Date format of `date_raw`. Defaults to DATE_FORMAT.

    Returns:
        str: Modified date, in standard format %Y-%m-%d.

    """
    dt = datetime.strptime(date_raw, date_format)
    dt = dt.replace(**replace_fields)
    return dt.strftime(DATE_FORMAT)


def list_timezones():
    return pytz.all_timezones


def localdatenow(tz: str = "utc", **kwargs):
    return localdate(tz, force_today=True, **kwargs)


def localdate(
    tz: str = "utc",
    force_today: bool = False,
    hour_limit: int = None,
    date_format: str = DATE_FORMAT,
    plus_days: int = None,
    as_datetime: bool = False,
    minus_days: int = 0,
):
    """Get local date.

    By default, gets date prior to execution.

    Args:
        tz (str, optional): Timezone name. Defaults to UTC.
        force_today (bool, optional): If True, return today's date regardles of `hour_limit` value.
        hour_limit (int, optional): If local time hour is lower than this, returned date is previous day.
                                    Defaults to None.
        date_format (str, optional): Format of output datetime. Uses default YYYY-mm-dd.
        plus_days (int, optional): Number of days to add to local date.
        as_datetime (bool, optional): Set to True to return the date as a datetime.
        minus_days (int, optional): Number of days to subtract. Defaults to 0.
    """
    if tz is None:
        local_time = datetime.now()
    else:
        tz = pytz.timezone(tz)
        local_time = datetime.now(tz=tz)
    if (
        (minus_days == 0)
        and (not force_today)
        and ((hour_limit is None) or (local_time.hour < hour_limit))
    ):
        local_time = local_time - timedelta(days=1)
    local_time = local_time - timedelta(days=minus_days)
    if plus_days:
        local_time += timedelta(days=plus_days)
    if as_datetime:
        return local_time
    return local_time.strftime(date_format)


def clean_date_series(
    ds: Union[pd.Series, list],
    format_input: str = None,
    format_output: str = DATE_FORMAT,
    as_datetime: bool = False,
    **kwargs
) -> Union[pd.Series, list]:
    is_list = isinstance(ds, list)
    if format_output is None:
        format_output = DATE_FORMAT
    ds_new = pd.to_datetime(ds, format=format_input, **kwargs)
    if is_list:
        ds_new = pd.Series(ds_new)
    if not as_datetime:
        ds_new = ds_new.dt.strftime(format_output)
    if is_list:
        return ds_new.tolist()
    return ds_new


@contextmanager
def _setlocale(name: str):
    # REF: https://stackoverflow.com/questions/18593661/how-do-i-strftime-a-date-object-in-a-different-locale
    # with LOCALE_LOCK:
    #     saved = locale.setlocale(locale.LC_TIME, DEFAULT_LOCALE)
    #     try:
    #         print("DEBUG -- try", name)
    #         yield locale.setlocale(locale.LC_TIME, name)
    #     finally:
    #         print("DEBUG -- finally", saved)
    #         locale.setlocale(locale.LC_TIME, saved)
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        # print("DEBUG -- init", saved)
        try:
            # print("DEBUG -- try", name)
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            # print("DEBUG -- finally", saved)
            locale.setlocale(locale.LC_ALL, saved)


def from_tz_to_tz(dt: datetime, from_tz: str = "UTC", to_tz: str = None):
    dt = dt.replace(tzinfo=pytz.timezone(from_tz))
    dt = dt.astimezone(pytz.timezone(to_tz))
    return dt
