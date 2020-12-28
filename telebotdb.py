import psycopg2


class Service:
    def __init__(self, _id, _name, _price):
        self.id = _id
        self.name = _name
        self.price = _price

    def __str__(self):
        return str(self.id) + " " + self.name + " " + str(self.price)

class Master:
    def __init__(self, _id, _name):
        self.id = _id
        self.name = _name

    def __str__(self):
        return str(self.id) + " " + self.name

class Time:
    def __init__(self, _id, _day, _hour, _mins):
        self.id = _id
        self.day = _day
        self.hour = _hour
        self.mins = _mins

    def __str__(self):
        return str(self.id) + " " + str(self.day) + " " + str(self.hour) + " " + str(self.mins)

class Order:
    def __init__(self, _user, _id_time, _id_service, _id_master):
        self.user = _user
        self.id_t = _id_time
        self.id_s = _id_service
        self.id_m = _id_master

    def __str__(self):
        return self.user + " " + str(self.id_t) + " " + str(self.id_s) + " " + str(self.id_m)

class Impact:
    def __init__(self, _id, _sumprice):
        self.id = _id
        self.sum = _sumprice

    def __str__(self):
        return str(self.id) + " " + str(self.sum)


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

def get_master_with_free_time():
    """Возвращает list мастеров со свободным временем"""
    con = make_connection()
    cursor = con.cursor()
    cursor.execute('select * from master where (select count(id_m) '
                   'from master_timetable ) <> (select count(id_m) '
                   'from successful_order);')
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

def get_order():
    """Возвращает list имеющихся в бд заказов"""
    con = make_connection()
    cursor = con.cursor()
    cursor.execute('select * from successful_order;')
    data = cursor.fetchall()
    con.close()
    orders = []
    for o in data:
        orders.append(Order(o[0], o[1], o[2], o[3]))
    return orders

def get_order_having_user(user):
    """Возвращает list имеющихся в бд заказов для конкретного юзера"""
    con = make_connection()
    cursor = con.cursor()
    cursor.execute("select * from successful_order where id_user = '%s';" % str(user))
    data = cursor.fetchall()
    con.close()
    orders = []
    for o in data:
        orders.append(Order(o[0], o[1], o[2], o[3]))
    return orders

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
    cursor.execute(' select twd.id_t, mt.id_m, twd.dw, time.time from master_timetable mt'
                   ' join time_with_day twd on mt.id_t = twd.id_t'
                   ' join time on time.id_time = twd.id_time'
                   ' where (mt.id_m, mt.id_t) not in (select id_m, id_t from successful_order);')
    data = cursor.fetchall()
    con.close()
    for d in data:
        days.append([d[1], Time(d[0], d[2], d[3].hour, d[3].minute)])
        #  чтобы получить данные из этого залупного метода нужно:
        #  его вызвать и чему-то присвоить: t = telebotdb.get_date_accessible() - это лист
        #  t[11] - одиннадцатый элемент списка
        #  t[11][0] - id мастера, t[11][1] - объект Time (см строку 15)
        #  t[11][1].day - день, t[11][1].hour - час, t[11][1].mins - минуты, t[11][1].id
        #  соре ребят изящнее не придумал
    return days

def get_date_having_master(id_m: int):
    """Возвращает list объектов Time с полями day, hour, minute
    доступного времени для имеющегося id мастера, неотсортировано"""
    days = []
    con = make_connection()
    cursor = con.cursor()
    cursor.execute(' select twd.id_t, twd.dw, time.time from master_timetable mt'
                   ' join time_with_day twd on mt.id_t = twd.id_t'
                   ' join time on time.id_time = twd.id_time'
                   ' where mt.id_m = %d'
                   ' and (mt.id_m, mt.id_t) not in (select id_m, id_t from successful_order);' % (id_m))
    data = cursor.fetchall()
    con.close()
    for d in data:
        days.append(Time(d[0], d[1], d[2].hour, d[2].minute))
        #  тут достать чуть проще, нету мастера:
        #  t = telebotdb.get_date_having_master(3) - это лист
        #  t[11] - одиннадцатый элемент
        #  t[11].day  .hour  .mins .id
    return days

def make_order(string_user, id_time, id_service, id_master):
    """Позволяет создать заказ в бд, без проверок, просто пуш"""
    con = make_connection()
    cursor = con.cursor()
    cursor.execute("insert into successful_order (id_user, id_t, id_service, id_m) values ('%s', %d, %d, %d);"
                   % (string_user, id_time, id_service, id_master));
    con.commit()
    con.close()

def delete_order(o: Order):
    con = make_connection()
    cursor = con.cursor()
    cursor.execute("delete from successful_order "
                   "where id_user = '%s' and id_t = %d and id_service = %d and id_m = %d;"
                   % (o.user, o.id_t, o.id_s, o.id_m));
    con.commit()
    con.close()

