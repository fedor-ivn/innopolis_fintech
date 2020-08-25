import datetime
from threading import Thread
from eth_hash.auto import keccak


def increase_time(curr_datetime: datetime):
    if curr_datetime.hour == 23:
        curr_datetime += datetime.timedelta(hours=1)
    else:
        curr_datetime += datetime.timedelta(hours=23)
    return curr_datetime


def create_hash(month, year, hash_):
    d = datetime.datetime(day=1, month=month, year=year, hour=23)
    while d.month == month:
        timestamp_bytes = int.to_bytes(int(d.timestamp()), 32, byteorder='big')
        str_ = str(keccak(timestamp_bytes).hex())
        if str_ == hash_:
            if d.hour == 23:
                d += datetime.timedelta(hours=1)
            print(d.strftime("%d.%m"))
            return 0
        else:
            d = increase_time(d)


def main():
    year = int(input())
    hash_ = input()

    t1 = Thread(target=create_hash, args=(1, year, hash_))
    t2 = Thread(target=create_hash, args=(2, year, hash_))
    t3 = Thread(target=create_hash, args=(3, year, hash_))
    t4 = Thread(target=create_hash, args=(4, year, hash_))
    t5 = Thread(target=create_hash, args=(5, year, hash_))
    t6 = Thread(target=create_hash, args=(6, year, hash_))
    t7 = Thread(target=create_hash, args=(7, year, hash_))
    t8 = Thread(target=create_hash, args=(8, year, hash_))
    t9 = Thread(target=create_hash, args=(9, year, hash_))
    t10 = Thread(target=create_hash, args=(10, year, hash_))
    t11 = Thread(target=create_hash, args=(11, year, hash_))
    t12 = Thread(target=create_hash, args=(12, year, hash_))

    threads = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
