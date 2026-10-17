"""Custom test runner with a Python 3.14 compatibility shim.

Django 5.0's BaseContext.__copy__() relies on `copy(super())`, which no longer
returns a shallow copy of the context instance on Python 3.13/3.14. Result:
the test client's template instrumentation crashes with
    AttributeError: 'super' object has no attribute 'dicts'
for every test that renders a template through the test client.

This shim restores a correct shallow copy of the context. It affects TESTS
ONLY (via TEST_RUNNER); the running server does not use this code path.

DELETE this shim once the project runs a Django version that supports
Python 3.14 (5.2.6+) — which first requires upgrading MariaDB to 10.5+
(Django 5.1+ dropped MariaDB 10.4 support).
"""

import sys

from django.test.runner import DiscoverRunner

if sys.version_info >= (3, 13):
    from django.template.context import BaseContext

    def _py314_safe_base_context_copy(self):
        duplicate = type(self).__new__(type(self))
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = _py314_safe_base_context_copy


class KCCDiscoverRunner(DiscoverRunner):
    """Default runner; exists only to host the compatibility shim above."""
