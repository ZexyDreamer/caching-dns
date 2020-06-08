import pickle
import datetime


def load_cache():
    try:
        with open('dns.cache', 'rb') as f:
            result = pickle.load(f)
        print(f'Кэш загружен')
    except Exception as e:
        print(f'Возникла ошибка при загрузке кэш-файла dns.cache: {e}')
        return
    return result


def save_cache():
    try:
        with open('dns.cache', 'wb') as f:
            pickle.dump(database, f)
        print(f'Закэшировано')
    except Exception as e:
        print(f'Возникла ошибка при сохранении: {e}')


def delete_old_records():
    delta = 0
    for key, value in database.items():
        last_length = len(value)
        database[key] = set(packet for packet in value if not datetime.datetime.now() - packet.create_time > datetime.timedelta(seconds=packet.resource_record.ttl))
        delta += last_length - len(database[key])
    if delta > 0:
        print(f'В {datetime.datetime.now()} удалено {delta} старых ресурсных записей')


database = load_cache()
