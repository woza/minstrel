
def ensure_array(item):
    try:
        junk = item[0]
    except TypeError:
        return [item]

    return item
