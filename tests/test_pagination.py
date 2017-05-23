import unittest
import sys
import os

try:
    from instagram_private_api_extensions import pagination
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api_extensions import pagination


class TestPagination(unittest.TestCase):
    """Tests for pagination related functions."""

    def test_page(self):
        testset = ['a', 'b', 'c', 'd', 'e', 'f', 'h', 'i', 'j', 'k', 'l', 'm', 'n']

        def paging_stub(start=0):
            page_size = 3
            result = {
                'items': testset[start:start + page_size]
            }
            if len(testset) > start + page_size:
                result['next_index'] = start + page_size
            return result

        resultset = []
        for results in pagination.page(
                paging_stub, args={},
                cursor_key='start',
                get_cursor=lambda r: r.get('next_index'),
                wait=0):
            if results.get('items'):
                resultset.extend(results['items'])
        self.assertEqual(testset, resultset)

        resultset = []
        for results in pagination.page(
                paging_stub, args={},
                cursor_key='start',
                get_cursor=lambda r: r.get('next_index'),
                wait=1):
            if results.get('items'):
                resultset.extend(results['items'])
        self.assertEqual(testset, resultset)
