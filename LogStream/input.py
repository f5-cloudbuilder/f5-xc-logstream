import json

from LogStream import storage_engine
import pytz
import datetime
import requests
import xmltodict


class F5XCGeneric (storage_engine.DatabaseFormat):
    def __init__(self, name, api_key, logger, timezone='Europe/London'):
        super(F5XCGeneric, self).__init__(logger)
        # Table
        self.type = 'f5xc'
        # Primary key
        self.id = name
        # Attribute
        self.api_key = api_key
        self._update_timezone(timezone)
        self.session = requests.session()

    def generate_error(self, r):
        if self.logger:
            self.logger.error('%s::%s: code %s; %s' %
                              (__class__.__name__, __name__, r.status_code, r.text))
        raise ConnectionError('%s::%s: code %s; %s' %
                              (__class__.__name__, __name__, r.status_code, r.text))

    def _get(self, host, path, parameters=None):
        # URL builder
        if parameters and len(parameters) > 0:
            uri = path + '?' + '&'.join(parameters)
        else:
            uri = path

        url = 'https://' + host + uri
        headers = {
            'Authorization': 'APIToken ' + self.api_key,
            'Content-Type': 'application/json'
        }
        r = self.session.get(
            url,
            headers=headers,
            verify=False)
        if r.status_code not in (200, 201, 202, 204):
            self.generate_error(r)

        return r.json()

    def _post(self, host, path, data):
        url = 'https://' + host + path
        headers = {
            'Authorization': 'APIToken ' + self.api_key,
            'Content-Type': 'application/json'
        }
        r = self.session.post(
            url,
            headers=headers,
            json=data,
            verify=False)

        if r.status_code not in (200, 201, 202, 204):
            self.generate_error(r)

        if r.text == '':
            return {}
        else:
            return r.json()

    @staticmethod
    def get_timezones():
        from pytz import common_timezones

        return common_timezones

    def _update_timezone(self, timezone):
        if timezone in F5XCGeneric.get_timezones():
            self.timezone = timezone
        else:
            raise KeyError('%s::%s: unknown timezone %s n' %
                           (__class__.__name__, __name__, timezone))

    def _update_time_now(self):
        return datetime.datetime.now(tz=pytz.timezone(self.timezone)).strftime("%Y-%m-%dT%H:%M:%SZ")


class F5XCNamespace (F5XCGeneric):
    def __init__(self, name, api_key, logger, start_time=None):
        super(F5XCNamespace, self).__init__(name, api_key, logger)
        # Table
        self.type = 'f5xc_namespace'
        # Primary key
        self.id = name
        # Attribute
        self.name = name
        if start_time is None:
            self.time_fetch_security_events = self._update_time_now()
        else:
            self.set_event_start_time(date=start_time)
        self.events = []
        self.filter = ''

    def set_event_start_time(self, date):
        """
        fetch security events whose timestamp >= start_time

        :param date: year, month, day, hour = 0, minute = 0, timezone = None
        """
        # Default values
        if 'hour' not in date.keys():
            date['hour'] = 0
        if 'minute' not in date.keys():
            date['minute'] = 0
        if 'timezone' in date.keys():
            self._update_timezone(date['timezone'])

        # set time
        self.time_fetch_security_events = datetime.datetime(date['year'], date['month'], date['day'], date['hour'], date['minute']).replace(tzinfo=pytz.timezone(self.timezone)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def fetch_security_events(self, host):
        # set timer
        start_time = self.time_fetch_security_events
        self.time_fetch_security_events = self._update_time_now()
        end_time = self.time_fetch_security_events

        # fetch security events
        path = "/api/data/namespaces/" + self.name + "/app_security/events"
        data = {
                "namespace": self.name,
                "scroll": True,
                "sort": "ASCENDING",
                "start_time": start_time,
                "end_time": end_time,
                "query": self.filter,
            }
        dirty_events = self._post(host, path, data)['events']

        # Clean
        for dirty_event in dirty_events:
            event = json.loads(dirty_event)
            event['req_headers'] = json.loads(event['req_headers'])
            if event['violation_details'] != '':
                event['violation_details'] = json.loads(json.dumps(xmltodict.parse(event['violation_details'])))
            self.events.append(event)

    def set_filter(self, event_filter):
        """
        query is used to specify the list of matchers syntax

        :param event_filter: dict. deep 1. Example: filter = {sni: 'www.f5dc.dev', src_ip: '34.77.162.20'}
        :return:
        """
        query = '{'
        first_element = True
        for key, value in event_filter.items():
            if first_element:
                query += key + '="' + value + '"'
                first_element = False
            else:
                query += ', ' + key + '="' + value + '"'
        query += '}'
        self.filter = query

    def get_security_events(self):
        return self.events

    def pop_security_events(self):
        data = self.events
        self.events = []
        return data

    def get_json(self):
        return {
            'name': self.id,
            'start_time_for_next_fetch_of_security_events': self.time_fetch_security_events,
        }


class F5XCTenant (F5XCGeneric):
    def __init__(self, name, api_key, logger):
        super(F5XCTenant, self).__init__(name, api_key, logger)
        # Table
        self.type = 'f5xc_tenant'
        # Primary key
        self.id = name
        # Relationship with other tables
        self.name = name
        self.children['f5xc_namespace'] = {}
        self.f5xc_namespace_ids = self.children['f5xc_namespace'].keys()
        self.f5xc_namespaces = self.children['f5xc_namespace'].values()
        # Attribute
        self.host = name + ".console.ves.volterra.io"

    def _create_namespace(self, name, api_key=None, start_time=None):
        if api_key is None:
            # Global API KEY for a Tenant
            api_key = self.api_key
        f5xc_namespace = F5XCNamespace(
            name=name,
            api_key=api_key,
            start_time=start_time,
            logger=self.logger)
        self.create_child(f5xc_namespace)

    def _delete_namespace(self, name):
        self.children['f5xc_namespace'][name].delete()

    def set_event_start_time(self, date):
        for f5xc_namespace in self.f5xc_namespaces:
            f5xc_namespace.set_event_start_time(date)

    def fetch_security_events(self):
        for f5xc_namespace in self.f5xc_namespaces:
            f5xc_namespace.fetch_security_events(host=self.host)

    def get_security_events(self):
        events = {}
        for f5xc_namespace in self.f5xc_namespaces:
            events[f5xc_namespace.name] = f5xc_namespace.get_security_events()
        return events

    def set_filter(self, event_filter, namespace=None):
        if namespace is None:
            for f5xc_namespace in self.f5xc_namespaces:
                f5xc_namespace.set_filer(event_filter)
        else:
            self.children['f5xc_namespace'][namespace].set_filter(event_filter)

    def pop_security_events(self):
        events = []
        for f5xc_namespace in self.f5xc_namespaces:
            events.extend(f5xc_namespace.pop_security_events())
        return events

    def get_json(self):
        data = {
            'name': self.name,
            'api_key': self.api_key,
            'namespaces': []
        }
        for f5xc_namespace_id, f5xc_namespace in self.children['f5xc_namespace'].items():
            data['namespaces'].append(f5xc_namespace.get_json())
        return data

    def get_namespaces(self):
        return self.f5xc_namespaces

    def set(self, data_json):
        self.id = data_json['name']
        self.name = data_json['name']
        self.host = data_json['name'] + ".console.ves.volterra.io"
        self.api_key = data_json['api_key']

        # start_time
        start_time = None
        if 'start_time' in data_json.keys():
            start_time = data_json['start_time']

        declaration_namespace_names = []
        # Create
        for namespace in data_json['namespaces']:
            declaration_namespace_names.append(namespace['name'])
            if namespace['name'] not in self.f5xc_namespace_ids:
                self._create_namespace(name=namespace['name'], start_time=start_time)

        # Delete
        for namespace in self.f5xc_namespaces:
            if namespace.name not in declaration_namespace_names:
                self._delete_namespace(name=namespace['name'])


def setup_logging(log_level, log_file):
    import logging

    if log_level == 'debug':
        log_level = logging.DEBUG
    elif log_level == 'verbose':
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(filename=log_file, format='%(asctime)s %(levelname)s %(message)s', level=log_level)
    return logging.getLogger(__name__)


# Start program
if __name__ == "__main__":

    import pprint
    """
    for common_timezone in F5XCGeneric.get_timezones():
        pprint.pprint(common_timezone)
    """

    logger = setup_logging(
        log_level='warning',
        log_file='logstream.log'
    )

    my_tenant = F5XCTenant(
        name="f5-emea-ent",
        api_key="DICHuadYFS6qVcHZsEd/Pt6ZsW0=",
        logger=logger
    )

    my_tenant._create_namespace(name="al-dacosta")

    my_tenant.set_event_start_time({
        "year": 2022,
        "month": 2,
        "day": 16,
        "hour": 0,
        "minute": 0,
        "timezone": "Europe/Paris"
    })

    my_tenant.set_filter(
        namespace="al-dacosta",
        event_filter={
            "sec_event_type": "waf_sec_event",
            "src_ip": "82.66.123.186"
        }
    )

    my_tenant.fetch_security_events()

    events = my_tenant.get_security_events()

    pprint.pprint(events['al-dacosta'][0])





