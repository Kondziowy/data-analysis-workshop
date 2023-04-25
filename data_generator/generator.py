from collections import OrderedDict
import logging
import random
import math
import typing
import sqlite3
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)


class GeneratorBase:
    # e.g. (x^8*sin(7*x))/(100*x^6)
    def generate(frequency_fun: typing.Callable,
                 start_date: datetime,
                 end_date: datetime) -> list[str]:
        raise NotImplementedError

# 127.0.0.1 - - [01/Apr/2023:11:27:40 +0000] "GET /index.html HTTP/1.1" 200 1200 0.002617
# 127.0.0.1 - - [01/Apr/2023:11:27:45 +0000] "GET /images/logo.png HTTP/1.1" 200 15734 0.007353
# 127.0.0.1 - - [01/Apr/2023:11:28:10 +0000] "POST /login HTTP/1.1" 302 - 0.014992
# 127.0.0.1 - - [01/Apr/2023:11:29:05 +0000] "GET /dashboard HTTP/1.1" 200 4369 0.100576
# 127.0.0.1 - - [01/Apr/2023:11:30:20 +0000] "GET /orders HTTP/1.1" 200 3520 0.006817


class ApacheGenerator(GeneratorBase):
    PATTERN = "{source_ip} - - [{timestamp}] \"{method_path} HTTP/1.1\"" \
              " {return_code} {response_size} {response_time}"
    TIMESTAMP_PATTERN = "01/Apr/2023:11:27:40 +0000"

    method_probabilities = OrderedDict({
        0.1: "GET /",
        0.2: "GET /static/favicon.ico",
        0.3: "GET /static/images/logo.png",
        0.4: "GET /static/style.css",
        0.5: "GET /static/bootstrap.min.js",
        0.6: "GET /static/jquery-3.3.1.slim.min.js",
        0.65: "POST /login",
        0.70: "POST /documents",
        0.75: "GET /documents?page=X&per_page=Y&filter=Z",
        0.80: "GET /document?id=X",
        0.85: "GET /users",
        0.90: "UPDATE /users/X",
        0.95: "POST /reviews?document_id=X",
        1: "GET /reviews?document_id=X"
    })

    status_probabilities = OrderedDict({
        0.7: "200",
        0.75: "403",
        0.8: "401",
        0.85: "500",
        0.9: "404",
        1.0: "502"

    })

    def _draw_method(self) -> str:
        method_seed = random.random()
        for key, value in self.method_probabilities.items():
            if method_seed < key:
                return value

    def _draw_status(self) -> str:
        method_seed = random.random()
        for key, value in self.status_probabilities.items():
            if method_seed < key:
                return value

    def generate(self, frequency_fun: typing.Callable, start_date: datetime, end_date: datetime,
                 length_fun: typing.Callable = random.random) -> list[str]:
        timestamp = start_date
        result = []
        while timestamp < end_date:
            timestamp += timedelta(seconds=1)
            draws = frequency_fun(timestamp)
            log.debug("Generating %s samples for ts %s", draws, timestamp)
            for _ in range(draws):
                # TODO: convert to yield
                method = self._draw_method()
                result.append(self.PATTERN.format(source_ip=f"192.168.{random.randrange(0,253)}.{random.randrange(0,253)}",
                                                          timestamp=timestamp.strftime("%d/%b/%Y:%H:%M:%S %z"),
                                                          method_path=method,
                                                          return_code=self._draw_status(),
                                                          response_size=int(100000 * random.random()) if "GET" in method else "",
                                                          response_time="%.3lf" % length_fun(timestamp, method)))

        return result


class PostgresGenerator(GeneratorBase):
    """
    SELECT relname, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch, n_tup_ins, n_tup_upd, n_tup_del
    FROM pg_stat_user_tables
    WHERE relname = 'orders';
        relname   | seq_scan | seq_tup_read | idx_scan | idx_tup_fetch | n_tup_ins | n_tup_upd | n_tup_del
    -------------+----------+--------------+----------+---------------+-----------+-----------+-----------
    customers   |        4 |         1000 |        1 |           100 |        50 |        20 |        10
    orders      |        2 |          500 |        2 |           200 |        30 |        40 |        20
    products    |        5 |         1500 |        3 |           300 |        80 |        10 |         5
    """


    def generate(self, frequency_fun: typing.Callable, start_date: datetime, end_date: datetime,
                 length_fun: typing.Callable = random.random) -> list[str]:   
        timestamp = start_date
        result = []
        tables = ['documents', 'permissions', 'users']
        initial_budget = 200
        current_budget = initial_budget
        while timestamp < end_date:
            timestamp += timedelta(seconds=5)
            # a bit of play
            current_budget = initial_budget + random.randint(-20, 20)
            for table in tables:
                tuples_read = random.randint(0, current_budget)
                current_budget -= tuples_read
                tuples_write = random.randint(0, current_budget)
                current_budget -= tuples_write
                result.append((timestamp.strftime("%Y-%m-%d %H:%M:%S.000"), table, tuples_read, tuples_write))
            if timestamp > datetime(2020,4,3,13,00,0, tzinfo=timezone.utc) and "audit_log" not in tables:
                tables.insert(0, "audit_log")
        return result



class PrometheusGenerator(GeneratorBase):
    """
    # HELP my_custom_metric A custom metric I created
    # TYPE my_custom_metric gauge
    my_custom_metric{label1="value1",label2="value2"} 42.0
    my_custom_metric{label1="value3",label2="value4"} 17.0

    # HELP http_requests_total The total number of HTTP requests
    # TYPE http_requests_total counter
    http_requests_total{method="GET",status="200"} 120
    http_requests_total{method="POST",status="200"} 35
    http_requests_total{method="GET",status="404"} 10
    http_requests_total{method="POST",status="404"} 2

    # HELP cpu_usage The current CPU usage as a percentage
    # TYPE cpu_usage gauge
    cpu_usage 75.0
    """
    pass

class GunicornGenerator(GeneratorBase):
    """
    [2022-04-01 13:37:00 +0000] [12345] [INFO] Listening at: http://0.0.0.0:8000 (12345)
    [2022-04-01 13:37:00 +0000] [12345] [INFO] Using worker: uvicorn.workers.UvicornWorker
    [2022-04-01 13:37:00 +0000] [12346] [INFO] Booting worker with pid: 12346
    [2022-04-01 13:37:01 +0000] [12346] [INFO] Started server process [12346]
    [2022-04-01 13:37:01 +0000] [12346] [INFO] Waiting for application startup.
    [2022-04-01 13:37:01 +0000] [12346] [INFO] Application startup complete.
    [2022-04-01 13:37:00 +0000] [12345] [ellen] [api.py:85] [INFO] GET /documents?page=X&per_page=Y&filter=Z 200 3520 0.006817
    [2022-04-01 13:37:00 +0000] [12345] [] [api.py:86] [INFO] Recording operation GET from user ellen
    [2022-04-01 13:37:00 +0000] [12345] [ellen] [api.py:85] [INFO] GET /users 200 3128 0.006817
    
    """
    pass


def frequency_function(d: datetime) -> int:
    # int((x**8 * math.sin(7 * x))/(100*x**6)) % 10
    multiplier = 1
    if d.hour > 8 and d.hour < 16:
        multiplier = abs(-0.25*(d.hour - 12)**2 + 2)
    return math.ceil(random.randrange(10) * multiplier)

def length_function(d: datetime, method: str) -> int:
    multiplier = 1
    if d.hour > 8 and d.hour < 16:
        multiplier = abs(-0.25*(d.hour - 12)**2 + 2)
    if d > datetime(2020,4,3,13,00,0, tzinfo=timezone.utc) and not "static" in method:
        multiplier = 4

    return multiplier * random.random()

if __name__ == '__main__':
    start = datetime(2020,4,2,8,0,0, tzinfo=timezone.utc)
    end = datetime(2020,4,3,16,10,0, tzinfo=timezone.utc)


    # g = ApacheGenerator()
    # result = g.generate(frequency_function, start, end, length_function)
    # with open("apache.log.big4", "w") as f:
    #     f.write("\n".join(result))

    p = PostgresGenerator()
    result = p.generate(frequency_function, start, end, length_function)
    print(f"Generated {len(result)} rows of sql data")
    conn = sqlite3.connect('tps_database.db')
    # TODO: check if table exists
    # print(result[:5])
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE if not exists db_activity (timestamp TEXT NOT NULL, table_name TEXT NOT NULL, tuples_read INTEGER NOT NULL, tuples_write INTEGER NULL)")
    for row in result:
        cursor.execute(f"INSERT INTO db_activity VALUES ('{row[0]}', '{row[1]}', {row[2]}, {row[3]})")
    conn.commit()
    # print(cursor.execute("SELECT * from db_activity").fetchone())