import requests
import re
import os
from html.parser import HTMLParser

_DISA_CRLS = "https://iasecontent.disa.mil/pki-pke/data/crls/dod_crldps.htm"


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


def write_crl(out_dir, crl_location):
    name = re.split("/", crl_location)[-1]
    crl = os.path.join(out_dir, name)
    with requests.get(crl_location, stream=True) as r:
        with open(crl, "wb") as crl_file:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    crl_file.write(chunk)


def refresh_crls(out_dir, logger=None):
    disa_html = fetch_disa()
    crl_list = crl_list_from_disa_html(disa_html)
    for crl_location in crl_list:
        if logger:
            logger.info("updating CRL from {}".format(crl_location))
        try:
            write_crl(out_dir, crl_location)
        except requests.exceptions.ChunkedEncodingError:
            if logger:
                logger.error(
                    "Error downloading {}, continuing anyway".format(crl_location)
                )


if __name__ == "__main__":
    import sys
    import datetime
    import logging

    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s]:%(levelname)s: %(message)s"
    )
    logger = logging.getLogger()
    logger.info("Updating CRLs")
    try:
        refresh_crls(sys.argv[1], logger=logger)
    except Exception as err:
        logger.exception("Fatal error encountered, stopping")
        sys.exit(1)
    logger.info("Finished updating CRLs")
