import logging
import socket
from datetime import datetime
from logging.handlers import SysLogHandler
from LogStream import storage_engine


class RemoteSyslog(storage_engine.DatabaseFormat):
    def __init__(self, ip_address, logger, port=514):
        super(RemoteSyslog, self).__init__(logger)
        # Table
        self.type = 'syslog'
        # Primary key
        self.id = ip_address + ':' + str(port)
        self.ip_address = ip_address
        self.port = port
        self.handler = logging.handlers.SysLogHandler(address=(ip_address, port), socktype=socket.SOCK_STREAM)
        self.handler.append_nul = False

    def emit(self, events):
        for event in events:
            struct_message = [
                'app=' + str(event['authority']),
                'bot_classification=' + str(event['bot_classification']),
                'bot_verification_failed=' + str(event['bot_verification_failed']),
                'browser_type=' + str(event['browser_type']),
                'attack_types=' + str(event['attack_types']),
                'component=' + str(event['req_path']),
                'correlation_id=' + str(event['messageid']),
                'description=' + str(event['vh_name']),
                'environment=' + str(event['tenant']),
                'gateway=' + str(event['src_site']),
                'http.hostname=' + str(event['req_headers']['Host']),
                'http.remote_addr=' + str(event['src_ip']),
                'http.remote_port=' + str(event['src_port']),
                'http.request_method=' + str(event['method']),
                'http.response_code=' + str(event['rsp_code']),
                'http.server_addr=' + str(event['dst_ip']),
                'http.server_port=' + str(event['dst_port']),
                'http.uri=' + str(event['req_headers']['Path']),
                'is_truncated=' + str(event['is_truncated_field']),
                'level=' + str(event['severity']),
                'policy_name=' + 'NotAvailable',
                'request=' + 'NotAvailable',
                'request_outcome=' + str(event['calculated_action']),
                'request_outcome_reason=' + 'NotAvailable',
                'signature_cves=' + 'NotAvailable',
                'signature_ids=' + 'NotAvailable',
                'signature_names=' + 'NotAvailable',
                'sub_violations=' + 'NotAvailable',
                'support_id=' + str(event['req_id']),
                'type=' + str(event['sec_event_type']),
                'version=' + str(event['http_version']),
                'violation_rating=' + 'NotAvailable',
                'violations=' + str(event['violations']),
                'x_forwarded_for_header_value=' + str(event['x_forwarded_for']),
                'event_host=' + str(event['hostname']),
                'event_source=' + str(event['site']),
                'event_sourcetype=' + str(event['source_type']),
                'event_time=' + str(event['time']),
            ]
            now = datetime.now()
            struct_message = now.strftime("%B %d %H:%M:%S") + " logstream logger: " + ';'.join(struct_message) + '\n'
            self.logger.debug("%s::%s: SEND LOG: %s" %
                              (__class__.__name__, __name__, struct_message))
            record = logging.makeLogRecord({
                'msg': struct_message,
            })
            self.handler.emit(record)

    def get_json(self):
        return {
            'ip_address': self.ip_address,
            'port': self.port
        }


class LogCollectorDB(storage_engine.DatabaseFormat):
    def __init__(self, logger):
        super(LogCollectorDB, self).__init__(logger)
        self.handlers = {}
        # Relationship with other tables
        self.children['syslog'] = {}

    def add(self, log_instance):
        if log_instance.id not in self.children[log_instance.type].keys():
            self.create_child(log_instance)

    def remove(self, log_instance):
        if log_instance.id in self.children[log_instance.type].keys():
            log_instance.delete()

    def get(self):
        data_all_types = {}

        # syslog
        type = 'syslog'
        data = []
        for log_instance in self.children[type].values():
            data.append(log_instance.get_json())
        data_all_types[type] = data

        return data_all_types

    def emit(self, events):
        # syslog
        type = 'syslog'
        for log_instance in self.children[type].values():
            log_instance.emit(events)



