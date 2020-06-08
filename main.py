import socket
from datetime import datetime
import dnslib
import caching

forwarder = '8.8.8.8'


def set_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 53))
    return sock


def send_response(response, address):
    sock.connect(address)
    sock.sendall(response)
    sock.close()


def get_cache_response(dns_record):
    print(f"Просматриваем кэш")
    key = (str(dns_record.q.qname).lower(), dns_record.q.qtype)
    if key in database and database[key]:
        response = dns_record.reply()
        response.rr = [p.resource_record for p in database[key]]
        print(f"Ответ получен из кэша\n{response}")
        return response
    print(f"В кэше такого нет")


def single_record(resource_record, date_time):
    key = (str(resource_record.rname).lower(), resource_record.rtype)
    if key in database:
        database[key].add((resource_record, date_time))
    else:
        database[key] = {(resource_record, date_time)}
    print(f'Добавлена новая запись:'
          f'\n{resource_record}')


def several_records(dns_record):
    for resource in dns_record.rr + dns_record.auth + dns_record.ar:
        date_time = datetime.now()
        single_record(resource, date_time)


def run_server():
    print(f'Сервер запущен')
    try:
        try:
            while True:
                data, addr = sock.recvfrom(2048)
                if database:
                    caching.delete_old_records()
                try:
                    dns_record = dnslib.DNSRecord.parse(data)
                    several_records(dns_record)
                except dnslib.DNSError as dns_error:
                    print(f'Возникла ошибка при разборе пакета: {dns_error}')
                    continue
                if not dns_record.header.qr:
                    response = get_cache_response(dns_record)
                    try:
                        if response:
                            send_response(response.pack(), addr)
                            if database:
                                caching.save_cache()
                        else:
                            resp = dns_record.send(forwarder)
                            several_records(dnslib.DNSRecord.parse(resp))
                            send_response(resp, addr)
                        set_socket()
                    except Exception as e:
                        print(f'Сервер не отвечает: {e}')
        except Exception as e:
            print(f'Ошибка сервера! {e}')
    except KeyboardInterrupt:
        exit(0)
    finally:
        if database:
            caching.save_cache()
        print(f'Сервер отключен')


if __name__ == '__main__':
    database = caching.database
    sock = set_socket()
    run_server()
