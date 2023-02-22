# GET https://api.jcdecaux.com/vls/v1/stations?contract={contract_name}&apiKey={api_key}

import requests
import traceback
import datetime
import time
import apilogin

APIKEY = apilogin.APIKEY
NAME = 'Dublin'
STATIONS = 'https://api.jcdecaux.com/vls/v1/stations'


def write_to_file(text, now):
    with open('data/bikes_{}'.format(now).replace(' ', '_'), 'w') as f:
        f.write(text)


# TODO
def write_to_db(text, now):
    pass


def main():
    try:
        now = datetime.datetime.now()
        r = requests.get(STATIONS, params={'apiKey': APIKEY, 'contract': NAME})
        print(r, now)
        write_to_file(r.text, now)
        write_to_db(r.text, now)
    except:
        print(traceback.format_exc())

        # TODO
        # if engine is None:
        #     pass

    return


main()