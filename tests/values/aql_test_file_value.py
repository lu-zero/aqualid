import sys
import time
import os.path

sys.path.insert(
    0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from aql_tests import AqlTestCase
from tests_utils import run_local_tests

from aql.utils import Tempfile
from aql.entity.aql_file_entity import FileChecksumEntity, FileTimestampEntity


class TestFileValue(AqlTestCase):

    def test_file_value(self):

        with Tempfile() as temp_file:
            test_string = '1234567890'

            temp_file.write(test_string.encode())
            temp_file.flush()

            temp_file_value1 = FileChecksumEntity(temp_file)
            temp_file_value2 = FileChecksumEntity(temp_file)

            self.assertEqual(temp_file_value1, temp_file_value2)
            self.assertTrue(temp_file_value1.is_actual())

            reversed_test_string = str(reversed(test_string))
            temp_file.seek(0)
            temp_file.write(reversed_test_string.encode())
            temp_file.flush()

            FileChecksumEntity(temp_file_value1)

            self.assertFalse(temp_file_value1.is_actual())

            temp_file_value2 = FileChecksumEntity(temp_file_value1)
            self.assertEqual(temp_file_value1.name, temp_file_value2.name)
            self.assertNotEqual(temp_file_value1, temp_file_value2)

    # ==========================================================

    def test_file_value_save_load(self):

        with Tempfile() as temp_file:
            test_string = '1234567890'

            temp_file.write(test_string.encode())
            temp_file.flush()

            temp_file_value = FileChecksumEntity(temp_file)

            self._test_save_load(temp_file_value)

        file_value = FileChecksumEntity(temp_file)
        self.assertEqual(temp_file_value.name, file_value.name)
        self.assertNotEqual(temp_file_value, file_value)
        self.assertFalse(file_value.is_actual())

    # ==========================================================

    def test_file_value_time(self):
        with Tempfile() as temp_file:
            test_string = '1234567890'

            temp_file.write(test_string.encode())
            temp_file.flush()

            temp_file_value1 = FileTimestampEntity(temp_file)
            temp_file_value2 = FileTimestampEntity(temp_file)

            self.assertEqual(temp_file_value1, temp_file_value2)

            time.sleep(2)
            temp_file.seek(0)
            temp_file.write(b"0987654321")
            temp_file.close()

            FileTimestampEntity(temp_file_value1.name)
            self.assertFalse(temp_file_value1.is_actual())

            temp_file_value2 = FileTimestampEntity(temp_file_value1)
            self.assertEqual(temp_file_value1.name, temp_file_value2.name)
            self.assertNotEqual(temp_file_value1, temp_file_value2)

    # ==========================================================

    def test_file_value_time_save_load(self):

        with Tempfile() as temp_file:
            test_string = '1234567890'

            temp_file.write(test_string.encode())
            temp_file.flush()

            temp_file_value = FileTimestampEntity(temp_file)

            self._test_save_load(temp_file_value)

        file_value = FileTimestampEntity(temp_file)
        self.assertEqual(temp_file_value.name, file_value.name)
        self.assertNotEqual(temp_file_value, file_value)
        self.assertFalse(file_value.is_actual())

    # ==========================================================

    def test_file_empty_value_save_load(self):

        value1 = FileChecksumEntity('__non_exist_file__')

        value2 = FileTimestampEntity(value1.name)

        self._test_save_load(value1)
        self._test_save_load(value2)

# ==========================================================

if __name__ == "__main__":
    run_local_tests()
