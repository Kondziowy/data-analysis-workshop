from collections import OrderedDict
import logging
import random
import time
import typing
from datetime import datetime, timedelta

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
        0.2: "GET /favicon.ico",
        0.3: "GET /images/logo.png",
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

    def generate(self, frequency_fun: typing.Callable, start_date: datetime, end_date: datetime) -> list[str]:
        timestamp = start_date
        result = []
        while timestamp < end_date:
            timestamp += timedelta(seconds=1)
            draws = frequency_fun(time.time())
            log.debug("Generating %s samples for ts %s", draws, timestamp)
            for _ in range(draws):
                result.append(self.PATTERN.format(source_ip="127.0.0.1",
                                                          timestamp=timestamp,
                                                          method_path=self._draw_method,
                                                          return_code=self._draw_status,
                                                          response_size=100000 * random.random(),
                                                          response_time="%.6lf" % random.random()))
                        
        return result
