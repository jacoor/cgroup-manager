from rest_framework.test import APITestCase
from cgroup_manager.cgroups.tests.mock_data import pids_list, pids_list_file_content_mock
from rest_framework.reverse import reverse
import mock
from subprocess import CalledProcessError
from urllib.parse import quote
# Create your tests here.

"""
    Test plan:
    1. API to create a new CGroup: POST -> create
    2. API to place process in cgroup: PUT -> edit
    3. API to list PID's in given cgroup: GET -> ListAPIView
"""


class APITestCase(APITestCase):

    def test_creating_new_cgroup(self):
        self.assertEqual(0, 1)

    def test_placing_pid_in_cgroup(self):
        self.assertEqual(0, 1)

    def test_listing_pids_for_cgroup(self):
        """
        Precise tests plan:

        1. test not existing cgroup/hierarchy - exceptions? 404.
        2. test existing
        """
        url = reverse("cgroup-process-list", args=["some-fake-cgroup"])
        with mock.patch("os.path.exists") as m:
            m.return_value = False
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

        with mock.patch("os.path.exists") as m:
            m.return_value = True
            with mock.patch("cgroup_manager.cgroups.api.open",
                            mock.mock_open(read_data=pids_list_file_content_mock)) as file_mock:
                url = reverse("cgroup-process-list", args=["real-group"])
                response = self.client.get(url)
                self.assertEqual(response.data, pids_list)
                file_mock.assert_called_once_with("/sys/fs/cgroup/real-group/tasks")

                # check nested deeper
                file_mock.reset_mock()
                url = reverse("cgroup-process-list", args=[quote("real-group/deeper", safe="")])
                response = self.client.get(url)
                self.assertEqual(response.data, pids_list)
                file_mock.assert_called_once_with("/sys/fs/cgroup/real-group/deeper/tasks")
