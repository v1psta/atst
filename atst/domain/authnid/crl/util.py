import requests
import re
import os
import pendulum
from html.parser import HTMLParser

_DISA_CRLS = "https://iasecontent.disa.mil/pki-pke/data/crls/dod_crldps.htm"

MODIFIED_TIME_BUFFER = 15 * 60


def fetch_disa():
    response = requests.get(_DISA_CRLS)
    return response.text


class DISAParser(HTMLParser):
    crl_list = []
    _CRL_MATCH = re.compile("DOD(ROOT|EMAIL|ID)?CA")

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = [pair[1] for pair in attrs if pair[0] == "href"].pop()
            if re.search(self._CRL_MATCH, href):
                self.crl_list.append(href)


def crl_list_from_disa_html(html):
    parser = DISAParser()
    parser.reset()
    parser.feed(html)
    return parser.crl_list


def crl_local_path(out_dir, crl_location):
    name = re.split("/", crl_location)[-1]
    crl = os.path.join(out_dir, name)
    return crl


def existing_crl_modification_time(crl):
    if os.path.exists(crl):
        prev_time = os.path.getmtime(crl)
        buffered = prev_time + MODIFIED_TIME_BUFFER
        mod_time = prev_time if pendulum.now().timestamp() < buffered else buffered
        dt = pendulum.from_timestamp(mod_time, tz="GMT")
        return dt.format("ddd, DD MMM YYYY HH:mm:ss zz")

    else:
        return False


def write_crl(out_dir, target_dir, crl_location):
    crl = crl_local_path(out_dir, crl_location)
    existing = crl_local_path(target_dir, crl_location)
    options = {"stream": True}
    mod_time = existing_crl_modification_time(existing)
    if mod_time:
        options["headers"] = {"If-Modified-Since": mod_time}

    with requests.get(crl_location, **options) as response:
        if response.status_code == 304:
            return False

        with open(crl, "wb") as crl_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    crl_file.write(chunk)

    return True


def remove_bad_crl(out_dir, crl_location):
    crl = crl_local_path(out_dir, crl_location)
    os.remove(crl)


def refresh_crls(out_dir, target_dir, logger):
    disa_html = fetch_disa()
    crl_list = crl_list_from_disa_html(disa_html)
    for crl_location in crl_list:
        logger.info("updating CRL from {}".format(crl_location))
        try:
            if write_crl(out_dir, target_dir, crl_location):
                logger.info("successfully synced CRL from {}".format(crl_location))
            else:
                logger.info("no updates for CRL from {}".format(crl_location))
        except requests.exceptions.ChunkedEncodingError:
            if logger:
                logger.error(
                    "Error downloading {}, removing file and continuing anyway".format(
                        crl_location
                    )
                )
            remove_bad_crl(out_dir, crl_location)


if __name__ == "__main__":
    import sys
    import logging

    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s]:%(levelname)s: %(message)s"
    )
    logger = logging.getLogger()
    logger.info("Updating CRLs")
    try:
        refresh_crls(sys.argv[1], sys.argv[2], logger)
    except Exception as err:
        logger.exception("Fatal error encountered, stopping")
        sys.exit(1)
    logger.info("Finished updating CRLs")
