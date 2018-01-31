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
        """
        Precise test plan:

        1. try to create cgroup in improper hierarchy - error, 400.
            a) error handling: mkdir -p will not work if the system is read only - and this is true
            if you try to create directory in /sys/fs/cgroup
        2. Create in proper hierarchy
            201 Created
        """
        url = reverse("cgroups", args=["fake-hierarchy"])

        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], {"cgroup_name is required"})

        with mock.patch("check_call") as m:
            m.side_effect = CalledProcessError(
                'Command \'["mkdir", "-p", "/sys/fs/cgroup/fake-hierarchy/some-cgroup"]\' '
                'returned non-zero exit status 1')
            response = self.client.post(url, {"cgroup_name": "some-cgroup"})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data["detail"], "Not existing hierarchy")
            m.assert_called_once_with(["mkdir", "-p", "/sys/fs/cgroup/fake-hierarchy/some-cgroup"])

            m.reset_mock()
            response = self.client.post(url, {"cgroup_name": "some-cgroup/nested_cgroup"})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data, "Not existing hierarchy")
            m.assert_called_once_with(["mkdir", "-p", "/sys/fs/cgroup/fake-hierarchy/some-cgroup"])

            m.reset_mock()
            m.side_effect = None
            m.return_value = 0
            response = self.client.post(url, {"cgroup_name": "some-cgroup"})
            self.assertEqual(response.status_code, 201)
            m.assert_called_once_with(["mkdir", "-p", "/sys/fs/cgroup/fake-hierarchy/some-cgroup"])

        self.assertEqual(0, 1)

    def test_placing_pid_in_cgroup(self):
        self.assertEqual(0, 1)

    def test_listing_pids_for_cgroup(self):
        url = reverse("cgroup-process-list", args=["some-fake-cgroup"])
        with mock.patch("os.path.exists") as m:
            m.return_value = False
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.data["detail"], "Not found.")  # to make sure it's DRF response

            m.reset_mock()
            url = reverse("cgroup-process-list", args=[quote("real-group/deeper", safe="")])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.data["detail"], "Not found.")  # to make sure it's DRF response

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
