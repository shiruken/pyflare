#!/home/pi/berryconda3/envs/pyflare/bin/python -u
import json, os
import requests
import logging
import logging.handlers


class Cloudflare:
    def __init__(self, key):
        self.endpoint = "https://api.cloudflare.com/client/v4"
        self.headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}

    def get_current_ip_address(self):
        r = requests.get("https://api.ipify.org/")
        return r.text

    def get_zone_id(self, zone):
        payload = {'name': zone}
        r = requests.get(self.endpoint + "/zones", headers=self.headers, params=payload)
        return r.json()['result'][0]['id']

    def get_dns_record(self, zone_id, record):
        payload = {'name': record}
        r = requests.get(self.endpoint + "/zones/" + zone_id + "/dns_records", headers=self.headers, params=payload)
        r = r.json()
        return (r['result'][0]['id'], r['result'][0]['content'])

    def update_record(self, zone_id, record_id, record, ttl, ip_address):
        payload = {'type': 'A', 'name': record,'ttl': ttl, 'content': ip_address}
        r = requests.put(self.endpoint + "/zones/" + zone_id + "/dns_records/" + record_id, headers=self.headers, data=json.dumps(payload))
        return r.json()

    def __call__(self, zone, record, ttl):
        zone_id = self.get_zone_id(zone)
        record_id, record_ip_address = self.get_dns_record(zone_id, record)
        current_ip_address = self.get_current_ip_address()
        if record_ip_address != current_ip_address:
            cf.update_record(zone_id, record_id, record, ttl, current_ip_address)
            return f"A record for {record} updated from {record_ip_address} to {current_ip_address}"
        else:
            return f"IP address for {record} remains unchanged ({record_ip_address})"

if __name__ == '__main__':

    LOG_FILENAME = 'cron.log'
    logger = logging.getLogger('pyflare')
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1e7, backupCount=0)
    formatter = logging.Formatter("%(asctime)s %(filename)s[%(process)d] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    try:
        with open(os.path.join(__location__, 'config.json')) as json_data_file:
            config = json.load(json_data_file)
        key = config['key']
        zone = config['zone']
        record = config['record']
        ttl = int(config['ttl'])
    except:
        logger.exception('Unable to load config file')

    try:
        cf = Cloudflare(key)
        logger.info(cf(zone,record,ttl))
    except:
        logger.exception(f'Failed updating DNS record for {record}')
