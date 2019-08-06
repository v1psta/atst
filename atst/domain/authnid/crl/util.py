import re
import os

import pendulum
import requests


class CRLNotFoundError(Exception):
    pass


MODIFIED_TIME_BUFFER = 15 * 60


CRL_LIST = [
    "http://crl.disa.mil/crl/DODROOTCA2.crl",
    "http://crl.disa.mil/crl/DODROOTCA3.crl",
    "http://crl.disa.mil/crl/DODROOTCA4.crl",
    "http://crl.disa.mil/crl/DODROOTCA5.crl",
    "http://crl.disa.mil/crl/DODIDCA_33.crl",
    "http://crl.disa.mil/crl/DODIDCA_34.crl",
    "http://crl.disa.mil/crl/DODIDSWCA_35.crl",
    "http://crl.disa.mil/crl/DODIDSWCA_36.crl",
    "http://crl.disa.mil/crl/DODIDSWCA_37.crl",
    "http://crl.disa.mil/crl/DODIDSWCA_38.crl",
    "http://crl.disa.mil/crl/DODIDCA_39.crl",
    "http://crl.disa.mil/crl/DODIDCA_40.crl",
    "http://crl.disa.mil/crl/DODIDCA_41.crl",
    "http://crl.disa.mil/crl/DODIDCA_42.crl",
    "http://crl.disa.mil/crl/DODIDCA_43.crl",
    "http://crl.disa.mil/crl/DODIDCA_44.crl",
    "http://crl.disa.mil/crl/DODIDSWCA_45.crl",
    "http://crl.disa.mil/crl/DODIDSWCA_46.crl",
    "http://crl.disa.mil/crl/DODIDSWCA_47.crl",
    "http://crl.disa.mil/crl/DODIDSWCA_48.crl",
    "http://crl.disa.mil/crl/DODIDCA_49.crl",
    "http://crl.disa.mil/crl/DODIDCA_50.crl",
    "http://crl.disa.mil/crl/DODIDCA_51.crl",
    "http://crl.disa.mil/crl/DODIDCA_52.crl",
    "http://crl.disa.mil/crl/DODIDCA_59.crl",
    "http://crl.disa.mil/crl/DODSWCA_53.crl",
    "http://crl.disa.mil/crl/DODSWCA_54.crl",
    "http://crl.disa.mil/crl/DODSWCA_55.crl",
    "http://crl.disa.mil/crl/DODSWCA_56.crl",
    "http://crl.disa.mil/crl/DODSWCA_57.crl",
    "http://crl.disa.mil/crl/DODSWCA_58.crl",
    "http://crl.disa.mil/crl/DODSWCA_60.crl",
    "http://crl.disa.mil/crl/DODSWCA_61.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_33.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_34.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_39.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_40.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_41.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_42.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_43.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_44.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_49.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_50.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_51.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_52.crl",
    "http://crl.disa.mil/crl/DODEMAILCA_59.crl",
    "http://crl.disa.mil/crl/DODINTEROPERABILITYROOTCA1.crl",
    "http://crl.disa.mil/crl/DODINTEROPERABILITYROOTCA2.crl",
    "http://crl.disa.mil/crl/USDODCCEBINTEROPERABILITYROOTCA1.crl",
    "http://crl.disa.mil/crl/USDODCCEBINTEROPERABILITYROOTCA2.crl",
    "http://crl.disa.mil/crl/DODNIPRINTERNALNPEROOTCA1.crl",
    "http://crl.disa.mil/crl/DODNPEROOTCA1.crl",
    "http://crl.disa.mil/crl/DMDNSIGNINGCA_1.crl",
    "http://crl.disa.mil/crl/DODWCFROOTCA1.crl",
]


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
        if response.status_code > 399:
            raise CRLNotFoundError()

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


def log_error(logger, crl_location):
    if logger:
        logger.error(
            "Error downloading {}, removing file and continuing anyway".format(
                crl_location
            )
        )


def refresh_crls(out_dir, target_dir, logger):
    for crl_location in CRL_LIST:
        logger.info("updating CRL from {}".format(crl_location))
        try:
            if write_crl(out_dir, target_dir, crl_location):
                logger.info("successfully synced CRL from {}".format(crl_location))
            else:
                logger.info("no updates for CRL from {}".format(crl_location))
        except requests.exceptions.ChunkedEncodingError:
            log_error(logger, crl_location)
            remove_bad_crl(out_dir, crl_location)
        except CRLNotFoundError:
            log_error(logger, crl_location)


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
