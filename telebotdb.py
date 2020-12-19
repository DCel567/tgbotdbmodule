import psycopg2


class Service:
    def __init__(self, _id, _name, _price):
        self.id = _id
        self.name = _name
        self.price = _price

class Master:
    def __init__(self, _id, _name):
        self.id = _id
        self.name = _name

class Time:
    def __init__(self, _day, _hour, _mins):
        self.day = _day
        self.hour = _hour
        self.mins = _mins


def make_connection():
    conn = psycopg2.connect(
        database="d346he5v2rbj5e",
        user="yjsaechrwvutfp",
        password="8887db18cd4323b6dd6ec4abe48d7e1a97ac00e6c37d25b63427fcbdcae10cdf",
        host="ec2-54-75-229-28.eu-west-1.compute.amazonaws.com",
        port="5432"
    )
    return conn

def get_master():
    """Возвращает list всех имеющихся в бд мастеров"""
    con = make_connection()
    cursor = con.cursor()
    cursor.execute('select * from master;')
    data = cursor.fetchall()
    con.close()
    masters = []
    for m in data:
        masters.append(Master(m[0], m[1]))
    return masters

def get_service():
    """Возвращает list имеющихся в бд сервисов"""
    con = make_connection()
    cursor = con.cursor()
    cursor.execute('select * from master;')
    data = cursor.fetchall()
    con.close()
    services = []
    for m in data:
        services.append(Master(m[0], m[1]))
    return services

def get_date_accessible():
    """Возвращает list объектов Time с полями day, hour, minute
        доступного времени среди всех мастеров, неотсортировано"""
    days = []
    con = make_connection()
    cursor = con.cursor()
    cursor.execute(' select twd.dw, time.time from master_timetable mt'
                   ' join time_with_day twd on mt.id_t = twd.id_t'
                   ' join time on time.id_time = twd.id_time'
                   ' where (mt.id_m, mt.id_t) not in (select id_m, id_t from successful_order);')
    data = cursor.fetchall()
    con.close()
    for d in data:
        days.append(Time(d[0], d[1].hour, d[1].minute))
    return days

def get_date_having_master(id_m: int):
    """Возвращает list объектов Time с полями day, hour, minute
    доступного времени для имеющегося id мастера, неотсортировано"""
    days = []
    con = make_connection()
    cursor = con.cursor()
    cursor.execute(' select twd.dw, time.time from master_timetable mt'
                   ' join time_with_day twd on mt.id_t = twd.id_t'
                   ' join time on time.id_time = twd.id_time'
                   ' where mt.id_m = %d'
                   ' and (mt.id_m, mt.id_t) not in (select id_m, id_t from successful_order);' % (id_m))
    data = cursor.fetchall()
    con.close()
    for d in data:
        days.append(Time(d[0], d[1].hour, d[1].minute))
    return days

def make_order(string_user, id_time, id_service, id_master):
    """Позволяет создать заказ в бд, без проверок, просто пуш"""
    con = make_connection()
    cursor = con.cursor()
    cursor.execute("insert into successful_order (id_user, id_t, id_service, id_m) values ('%s', %d, %d, %d)"
                   % (string_user, id_time, id_service, id_master));
    con.commit()
    con.close()

