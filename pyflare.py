#! /usr/bin/python
import json, os

import requests

class Cloudflare:
    def __init__(self, key):
        self.endpoint = "https://api.cloudflare.com/client/v4"
        self.headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}

    def getmyip(self):
        r = requests.get("https://api.ipify.org/")
        return r.text

    def user(self):
        r = requests.get(self.endpoint + "/user", headers=self.headers)
        return r.json()

    def zones(self, zone):
        payload = {'name': zone}
        r = requests.get(self.endpoint + "/zones", headers=self.headers, params=payload)
        return r.json()

    def dns_records(self, zone_id, record):
        payload = {'name': record}
        r = requests.get(self.endpoint + "/zones/" + zone_id + "/dns_records", headers=self.headers, params=payload)
        return r.json()

    def update_record(self, zone_id, record_id, record, ttl, ip_address):
        payload = {'type': 'A', 'name': record,'ttl': ttl, 'content': ip_address}
        r = requests.put(self.endpoint + "/zones/" + zone_id + "/dns_records/" + record_id, headers=self.headers, data=json.dumps(payload))
        return r.json()

    def __call__(self,zone,record,ttl):
        zone_id = cf.zones(zone)['result'][0]['id']
        record_id = cf.dns_records(zone_id, record)['result'][0]['id']
        cf_ip_address = cf.dns_records(zone_id, record)['result'][0]['content']
        ip_address = cf.getmyip()
        if cf_ip_address != ip_address:
            try:
                cf.update_record(zone_id, record_id, record, ttl, ip_address)
                return f"A name record for {record} updated from {cf_ip_address} to {ip_address}"
            except:
                return f"Error updating A name record for {record} from {cf_ip_address} to {ip_address}"
        else:
            return f"IP address for {record} remains unchanged ({cf_ip_address})"

if __name__ == '__main__':
	__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
	try:
		with open(os.path.join(__location__,'config.json')) as json_data_file:
			config = json.load(json_data_file)
			key = config['key']
			zone = config['zone']
			record = config['record']
			ttl = int(config['ttl'])
		cf = Cloudflare(key)
		print(cf(zone,record,ttl))
	except IOError:
		print("Unable to find config file.")
