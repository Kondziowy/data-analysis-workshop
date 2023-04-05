import datetime
import unittest

# VSCode is lame and cannot set PYTHONPATH for pytest
import sys
sys.path.insert(0, '.')

from data_generator.generator import ApacheGenerator

class TestGenerator(unittest.TestCase):
    def test_generate_simple(self):
        start = datetime.datetime(2020,4,3,12,0,0)
        end = datetime.datetime(2020,4,3,12,1,0)
        frequency_fun = lambda x: 1

        g = ApacheGenerator()
        result = g.generate(frequency_fun, start, end)

        assert len(result) == 60