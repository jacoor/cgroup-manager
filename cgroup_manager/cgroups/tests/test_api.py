from subprocess import CalledProcessError
from urllib.parse import quote

import mock
from cgroup_manager.cgroups.tests.mock_data import pids_list, pids_list_file_content_mock
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


"""
    Test plan:
    2. API to place process in cgroup: PUT -> edit
"""


class APITestCase(APITestCase):

    def test_creating_new_cgroup(self):
        url = reverse("cgroups", args=["fake-hierarchy"])

        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'cgroup_path_fragment': ['This field is required.']})

        with mock.patch("cgroup_manager.cgroups.api.check_call") as m:
            m.side_effect = CalledProcessError(
                returncode=1, cmd=["mkdir", "-p", "/sys/fs/cgroup/fake-hierarchy/some-cgroup"])
            response = self.client.post(url, {"cgroup_path_fragment": "some-cgroup"})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.data["errors"][0],
                'Creating cgroup returned an error. Please check hierarchy and cgroup name.'
            )
            m.assert_called_once_with(["mkdir", "-p", "/sys/fs/cgroup/fake-hierarchy/some-cgroup"])

            m.reset_mock()
            response = self.client.post(url, {"cgroup_path_fragment": "some-cgroup/nested_cgroup"})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.data["errors"][0],
                'Creating cgroup returned an error. Please check hierarchy and cgroup name.'
            )
            m.assert_called_once_with(["mkdir", "-p", "/sys/fs/cgroup/fake-hierarchy/some-cgroup/nested_cgroup"])

            # success
            m.reset_mock()
            m.side_effect = None
            m.return_value = 0
            response = self.client.post(url, {"cgroup_path_fragment": "some-cgroup"})
            m.assert_called_once_with(["mkdir", "-p", "/sys/fs/cgroup/fake-hierarchy/some-cgroup"])
            self.assertEqual(response.status_code, 201)

    def test_placing_pid_in_cgroup(self):
        # sudo echo <task-process-id> >/cgroup/memory/group1/tasks
        # put and patch. Shold basically do the same in this situation.
        url = reverse("cgroup-processes", args=[quote("fake-hierarchy/some-cgroup", safe="")])
        with mock.patch("cgroup_manager.cgroups.serializers.check_if_process_exists") as m:
            # not existing process
            m.return_value = False
            response = self.client.put(url, data={"pid": 11})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data, {'pid': ['Process does not exist.']})

            # not existing cgroup
            m.reset_mock()
            m.return_value = True
            with mock.patch("cgroup_manager.cgroups.api.check_call") as echo_mock:
                echo_mock.side_effect = CalledProcessError(
                    returncode=1, cmd=["echo", 11, ">", "/sys/fs/cgroup/fake-hierarchy/some-cgroup/tasks"])
                response = self.client.put(url, data={"pid": 11})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    response.data["errors"][0],
                    'Adding process to cgroup failed. Please check hierarchy and cgroup name.'
                )
                echo_mock.assert_called_once_with(
                    ["echo", 11, ">", "/sys/fs/cgroup/fake-hierarchy/some-cgroup/tasks"])

                # fail, pid out of range
                echo_mock.reset_mock()
                echo_mock.return_value(0)
                echo_mock.side_effect = None
                response = self.client.put(url, data={"pid": 0})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data["pid"], ['Ensure this value is greater than or equal to 1.'])

                echo_mock.reset_mock()
                response = self.client.put(url, data={"pid": 32769})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data["pid"], ['Ensure this value is less than or equal to 32768.'])

                # success
                echo_mock.reset_mock()
                response = self.client.put(url, data={"pid": 11})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data["pid"], 11)

    def test_listing_pids_for_cgroup(self):
        url = reverse("cgroup-processes", args=["some-fake-cgroup"])
        with mock.patch("os.path.exists") as m:
            m.return_value = False
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.data["detail"], "Not found.")  # to make sure it's DRF response

            m.reset_mock()
            url = reverse("cgroup-processes", args=[quote("real-group/deeper", safe="")])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.data["detail"], "Not found.")  # to make sure it's DRF response

        with mock.patch("os.path.exists") as m:
            m.return_value = True
            with mock.patch("cgroup_manager.cgroups.api.open",
                            mock.mock_open(read_data=pids_list_file_content_mock)) as file_mock:
                url = reverse("cgroup-processes", args=["real-group"])
                response = self.client.get(url)
                self.assertEqual(response.data, pids_list)
                file_mock.assert_called_once_with("/sys/fs/cgroup/real-group/tasks")

                # check nested deeper
                file_mock.reset_mock()
                url = reverse("cgroup-processes", args=[quote("real-group/deeper", safe="")])
                response = self.client.get(url)
                self.assertEqual(response.data, pids_list)
                file_mock.assert_called_once_with("/sys/fs/cgroup/real-group/deeper/tasks")
