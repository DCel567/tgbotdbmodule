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

class Impact:
    def __init__(self, _id, _sumprice):
        self.id = _id
        self.sum = _sumprice


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
    cursor.execute('select * from service;')
    data = cursor.fetchall()
    con.close()
    services = []
    for m in data:
        services.append(Service(m[0], m[1], m[2]))
    return services

def get_impact_by_service():
    """Возвращает list айдишников сервисов и сумму сделанных по этому айди заказов"""
    con = make_connection()
    cursor = con.cursor()
    cursor.execute('select service.id_service, sum(service.price) '
                   'from service '
                   'INNER JOIN successful_order so '
                   'ON service.id_service = so.id_service '
                   'group by service.id_service;')
    data = cursor.fetchall()
    con.close()
    impacts = []
    for m in data:
        impacts.append(Impact(m[0], m[1]))
    return impacts

def get_impact_by_master():
    """Возвращает list айдишников мастеров и сумму сделанных по этому айди заказов"""
    con = make_connection()
    cursor = con.cursor()
    cursor.execute('select so.id_m, sum(service.price) '
                   'from service '
                   'INNER JOIN successful_order so '
                   'ON service.id_service = so.id_service '
                   'group by so.id_m;')
    data = cursor.fetchall()
    con.close()
    impacts = []
    for m in data:
        impacts.append(Impact(m[0], m[1]))
    return impacts

def get_date_accessible():
    """Возвращает list объектов Time с полями day, hour, minute
        доступного времени среди всех мастеров, неотсортировано"""
    days = []
    con = make_connection()
    cursor = con.cursor()
    cursor.execute(' select mt.id_m, twd.dw, time.time from master_timetable mt'
                   ' join time_with_day twd on mt.id_t = twd.id_t'
                   ' join time on time.id_time = twd.id_time'
                   ' where (mt.id_m, mt.id_t) not in (select id_m, id_t from successful_order);')
    data = cursor.fetchall()
    con.close()
    for d in data:
        days.append([d[0], Time(d[1], d[2].hour, d[2].minute)])
        #  чтобы получить данные из этого залупного метода нужно:
        #  его вызвать и чему-то присвоить: t = telebotdb.get_date_accessible() - это лист
        #  t[11] - одиннадцатый элемент списка
        #  t[11][0] - id мастера, t[11][1] - объект Time (см строку 15)
        #  t[11][1].day - день, t[11][1].hour - час, t[11][2].mins - минуты
        #  соре ребят изящнее не придумал
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
        #  тут достать чуть проще, нету мастера:
        #  t = telebotdb.get_date_having_master(3) - это лист
        #  t[11] - одиннадцатый элемент
        #  t[11].day  .hour  .mins
    return days

def make_order(string_user, id_time, id_service, id_master):
    """Позволяет создать заказ в бд, без проверок, просто пуш"""
    con = make_connection()
    cursor = con.cursor()
    cursor.execute("insert into successful_order (id_user, id_t, id_service, id_m) values ('%s', %d, %d, %d);"
                   % (string_user, id_time, id_service, id_master));
    con.commit()
    con.close()

