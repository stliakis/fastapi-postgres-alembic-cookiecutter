import random
import time
from datetime import datetime, timedelta
from optparse import OptionParser
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID
import traceback
from jose import jwt
from pydantic import BaseModel

from app.config import settings
import json
import os
import re
from datetime import datetime
from json import JSONDecodeError

from deepmerge import Merger
from pydantic import BaseModel
from starlette.datastructures import MultiDict


def dict_cache(cache: dict, key, result: callable):
    if key in cache:
        return cache[key]

    rv = result()
    cache[key] = rv
    return rv


def random_str(size=8, digits=False):
    import random
    import string
    if not digits:
        return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(size))
    else:
        return ''.join(random.SystemRandom().choice(string.digits) for _ in range(size))


class Timeit(object):
    def __init__(self, level, tag):
        self.tag = tag
        self.level = level
        self.begin = time.time()

    def __enter__(self):
        return self.begin

    def __exit__(self, type, value, traceback):
        log(self.level, "Timeit(context) -> %s   took %s ms" % (
            self.tag,
            round((time.time() - self.begin) * 1000, 2)
        ))


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def all_subclasses(cls):
    subs = cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]
    return subs


def default_ns_id():
    return random.SystemRandom().randint(0, 1000000000000)


def dictify(d):
    """Parses a dict and replaces objects with their .to_dict value"""
    if isinstance(d, list):
        return [
            dictify(i) for i in d
        ]

    if not isinstance(d, dict):
        if hasattr(d, "to_dict"):
            return dictify(d.to_dict())
        elif isinstance(d, set):
            return list(d)
        else:
            import datetime
            if isinstance(d, datetime.datetime):
                return datetime_to_stamp(d)
            elif isinstance(d, set):
                return list(d)
            return d

    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = dictify(v)
        elif isinstance(v, list):
            d[k] = [dictify(i) for i in v]
        elif isinstance(v, set):
            d[k] = [dictify(i) for i in v]
        elif isinstance(v, object) and hasattr(v, "to_dict"):
            d[k] = dictify(v.to_dict())
        else:
            import datetime
            if isinstance(v, datetime.datetime):
                d[k] = datetime_to_stamp(v)
            elif isinstance(v, set):
                d[k] = list(v)

    return d


def pydantic_errors_to_human_strings(errors):
    missing_fields = []
    for error in errors:
        if error.get("type") in ("value_error.missing", "type_error.none.not_allowed"):
            missing_fields.extend(error.get("loc"))
        else:
            log("warning", "error is not handled: {}".format(error))

    human_errors = []

    if missing_fields:
        human_errors.append("missing field(s) <{}>".format(", ".join(missing_fields)))

    return human_errors


def date_to_grouping_format(date, grouping):
    if grouping in ["day"]:
        return date.strftime('%d-%m-%Y')
    if grouping in ["week"]:
        return "{} - {}".format(date.strftime('%d-%m-%Y'), (date + timedelta(days=7)).strftime('%d-%m-%Y'))
    elif grouping == "hour":
        return date.strftime('%d-%m-%Y %H:%M')
    elif grouping == "month":
        return date.strftime('%m-%Y')
    else:
        return date.strftime('%d-%m-%Y')


def dictify_model(instance, model: BaseModel):
    fields = model.schema().get("properties").keys()
    return {
        k: getattr(instance, k, None) for k in fields
    }


def repr_string(instance, fields):
    fields = ", ".join(["%s=%s" % (field, getattr(instance, field)) for field in fields])
    return f"{instance.__class__.__name__}[{fields}]"


def print_stack_trace():
    traceback.print_stack()


def requests_response_to_curl(res):
    req = res.request
    command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
    method = req.method
    uri = req.url
    data = req.body
    headers = ['"{0}: {1}"'.format(k, v) for k, v in req.headers.items()]
    headers = " -H ".join(headers)
    return command.format(method=method, headers=headers, data=data, uri=uri)


def get(list, index, default=None):
    if len(list) >= index:
        return default
    return list[index]


def lmap(func, *iterable):
    return list(map(func, *iterable))


def parse_time_string(time_string):
    total_seconds = 0

    # Split the time string by spaces
    time_parts = time_string.split(' ')

    # Iterate over each time part
    for time_part in time_parts:
        # Extract the value and unit from the time part
        value = int(time_part[:-1])
        unit = time_part[-1]

        # Convert the unit to a timedelta argument
        if unit == 's':
            delta = timedelta(seconds=value)
        elif unit == 'm':
            delta = timedelta(minutes=value)
        elif unit == 'h':
            delta = timedelta(hours=value)
        elif unit == 'd':
            delta = timedelta(days=value)
        elif unit == 'w':
            delta = timedelta(weeks=value)
        elif unit == 'M':
            delta = timedelta(days=value * 30)  # Use 30 days per month as an approximation
        elif unit == 'y':
            delta = timedelta(days=value * 365)  # Use 365 days per year as an approximation
        else:
            raise ValueError(f'Invalid unit: {unit}')

        # Add the delta to the total number of seconds
        total_seconds += delta.total_seconds()

    return int(total_seconds)


def merge(a, b):
    my_merger = Merger(
        [
            (list, ["append"]),
            (dict, ["merge"]),
            (set, ["union"])
        ],
        ["override"],
        ["override"]
    )
    return my_merger.merge(a, b)


def multimerge(*dicts):
    rv = dicts[0]
    for d in dicts[1:]:
        rv = merge(rv, d)
    return rv


def prid(d, message=None):
    from app.config import settings
    if message:
        print(message)
    print(json_dump_all(d, indent=4, sort_keys=True))


def get(list, i, default=None):
    return list[i] if (list and i < len(list) and i >= 0) else default


def default(obj):
    import datetime
    if isinstance(obj, datetime.datetime):
        return datetime_to_stamp(obj)
    elif isinstance(obj, BaseModel):
        return obj.dict()
    elif hasattr(obj, "to_dict") and obj.to_dict:
        return obj.to_dict()
    elif isinstance(obj, set):
        return list(obj)
    return "(njs:%s)" % (str(obj))


def listify(to_list, ignore_none=False):
    # type: (object) -> object
    if ignore_none and to_list is None:
        return []
    if isinstance(to_list, list):
        return to_list
    return [to_list]


def datetime_to_stamp(obj):
    import calendar
    if obj.utcoffset() is not None:
        obj = obj - obj.utcoffset()
    millis = int(
        calendar.timegm(obj.timetuple()) * 1000 +
        obj.microsecond / 1000
    )
    return millis


def date_to_string(date, format="%Y-%m-%d %H:%M:%S"):
    if isinstance(date, str):
        return date

    if not date: return None
    string = None
    for f in listify(format):
        try:
            string = date.strftime(f).replace('X0', '').replace('X', '')
        except:
            pass
    if not string:
        raise Exception("bad format %s,%s" % (date, format))
    delimiter = None
    if "-" in format:
        delimiter = "-"
    elif "/" in format:
        delimiter = "/"
    if delimiter:
        string = delimiter.join([len(i) == 1 and "0%s" % i or i for i in string.split(delimiter)])
    date = string.replace("/0", "/")
    if date.startswith("0"):
        date = date[1:]
    return date


def date_from_epoch(epoch):
    epoch = float(epoch)
    try:
        return datetime.fromtimestamp(epoch)
    except ValueError as ex:
        return datetime.fromtimestamp(epoch / 1000)


def string_to_date(date, format=None):
    format = format or ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ",
                        "%Y-%m-%dT%H:%M:%S.%f"]

    if isinstance(date, datetime):
        return date
    format = listify(format)
    for f in format:
        try:
            return datetime.strptime(date, f.replace("X", ""))
        except:
            pass
    raise Exception("bad format? %s , available: %s" % (date, format))


def anything_to_date(anything):
    if not anything:
        return None

    if isinstance(anything, datetime):
        return anything

    try:
        epoch = float(anything)
        return date_from_epoch(epoch)
    except Exception as ex:
        return string_to_date(anything, ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ",
                                         "%Y-%m-%dT%H:%M:%S.%f", "%d/%m/%Y", "%m/%d/%Y %H:%M:%S"])

    return None


def get(alist, i, default=None):
    return alist[i] if (alist and i < len(alist) and i >= 0) else default


def listify(to_list, ignore_none=False):
    if ignore_none and to_list is None:
        return []
    if isinstance(to_list, list):
        return to_list
    return [to_list]


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def multidict_from_query_string(q):
    if "|" in q and "&" not in q:
        q = q.replace("|", "&")

    md = MultiDict()
    for i in q.split("&"):
        parts = i.split("=")
        key = parts[0]
        value = "=".join(parts[1:])
        md.add(key, value)

    return md


subclasses_cache = {}


def all_subclasses(cls):
    if cls in subclasses_cache:
        return subclasses_cache[cls]

    subs = cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]
    subclasses_cache[cls] = subs
    return subs


def random_str(size=8, digits=False):
    import random
    import string
    if not digits:
        return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(size))
    else:
        return ''.join(random.SystemRandom().choice(string.digits) for _ in range(size))


def clear(ob, null_value=None):
    """
    Remove the value that equal to "null_value"
    :param ob:
    :param null_value:
    :return:
    """
    if isinstance(ob, list):
        if null_value == "empty":
            return [i for i in ob if i]
        else:
            return [i for i in ob if i is not null_value]
    elif isinstance(ob, dict):
        if null_value == "empty":
            return {k: v for k, v in ob.items() if v}
        else:
            return {k: v for k, v in ob.items() if v is not null_value}


def json_dump_all(dic, ensure_ascii=None, **kwargs):
    return json.dumps(dic, default=None if kwargs.get("cls") else default, ensure_ascii=ensure_ascii or False, **kwargs)


class ClassPropertyDescriptor(object):
    def __init__(self, fget, fset=None):
        # type: (object, object) -> object
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def get_json_from_request(request):
    try:
        return request.json()
    except JSONDecodeError:
        return {}


def to_base64(input):
    import base64
    return base64.b64encode(str(input).encode()).decode('utf-8')


def from_base64(input):
    import base64
    return base64.b64decode(str(input).encode()).decode('utf-8')


def read_bulk_or_not(payload):
    if payload.get("requests"):
        return payload.get("requests")
    else:
        return [payload]


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_database_url_from_env():
    # copied from the alembic env.get_url
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    server = os.getenv("POSTGRES_SERVER", "db")
    db = os.getenv("POSTGRES_DB", "app")
    return f"postgresql://{user}:{password}@{server}/{db}"
