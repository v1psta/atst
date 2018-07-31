import re


# TODO: our sample SDN does not have an email address
def parse_sdn(sdn):
    try:
        parts = sdn.split(",")
        cn_string = [piece for piece in parts if re.match("^CN=", piece)][0]
        cn = cn_string.split("=")[-1]
        info = cn.split(".")
        return {"last_name": info[0], "first_name": info[1], "dod_id": info[-1]}
    except (IndexError, AttributeError):
        raise ValueError("'{}' is not a valid SDN".format(sdn))
