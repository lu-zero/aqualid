import sys
import os.path

sys.path.insert(
    0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from aql_tests import AqlTestCase
from tests_utils import run_local_tests

from aql.util_types import Dict, split_dict_type, value_dict_type

# ==============================================================================


class TestDictTypes(AqlTestCase):

    def test_dict(self):

        v = {1: 2, 3: '4'}

        d = Dict(v)
        self.assertEqual(d, v)

        d = Dict(v.items())
        self.assertEqual(d, v)

        d += ((4, '8'),)
        v.update(((4, '8'),))
        self.assertEqual(d, v)

        d += ((4, '8'),)
        v[4] = '88'

        self.assertEqual(d, v)

        self.assertEqual(Dict(), {})
        self.assertEqual(Dict(None), {})
        self.assertEqual(Dict(NotImplemented), {})

    # -----------------------------------------------------------

    def test_splitdict(self):

        v = {'1': '2', '3': '4'}
        vs = "1=2, 3=4"

        d = split_dict_type(Dict, separators=', ')(vs)
        self.assertEqual(d, v)

        d.update("a=7,c=9")
        v['a'] = '7'
        v['c'] = '9'
        self.assertEqual(d, v)
        self.assertEqual(str(d), "1=2,3=4,a=7,c=9")

    # -----------------------------------------------------------

    def test_value_dict_type(self):

        v = {'1': '2', '3': '4'}
        vs = "1=2, 3=4"

        d = value_dict_type(Dict, int, int)(v)
        self.assertEqual(d['1'], 2)
        self.assertEqual(d[3], 4)

        ds = split_dict_type(type(d), separators=', ')(vs)

        self.assertEqual(d, ds)

        ds[2] = 1
        ds.update(((2, 1),))

        ds.update("7=8")

        self.assertEqual(ds[7], 8)
        self.assertRaises(ValueError, ds.__setitem__, 'a', 4)
        self.assertRaises(ValueError, ds.__setitem__, 1, 'b')
        self.assertIn(3, ds)
        self.assertEqual(ds.setdefault(5, 10), 10)
        self.assertEqual(ds.get(5), 10)
        self.assertEqual(ds.setdefault(2, '0'), 1)

        self.assertEqual(ds[7], 8)


# ==============================================================================

if __name__ == "__main__":
    run_local_tests()
