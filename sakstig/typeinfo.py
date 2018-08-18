def is_str(o):
    return hasattr(o, 'lower')
def is_regexp(o):
    return hasattr(i, 'search')
def is_dict(o):
    return hasattr(o, 'values')
def is_list(o):
    return hasattr(o, '__iter__') and not is_dict(o) and not is_str(o)
def is_set(o):
    return hasattr(o, 'union')
def is_int(o):
    return hasattr(o, 'real') and not hasattr(o, 'is_integer') and not isinstance(o, bool)
def is_float(o):
    return hasattr(o, 'is_integer') and not isinstance(o, bool)
def is_timedelta(o):
    return hasattr(o, 'total_seconds')
def is_datetime(o):
    return hasattr(o, 'year') and hasattr(o, 'hour')
def is_date(o):
    return hasattr(o, 'year') and not hasattr(o, 'hour')
def is_time(o):
    return not hasattr(o, 'year') and hasattr(o, 'hour')    
