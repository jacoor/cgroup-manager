from cgroup_manager.cgroups.utils import check_if_process_exists
from django.test import TestCase


class TestUtils(TestCase):

    def test_if_process_exists(self):
        # not testing success - not needed, too simple
        self.assertFalse(check_if_process_exists("not a number"))
