from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import os
from rest_framework.exceptions import NotFound
from urllib.parse import unquote


cgroup_path_prefix = "/sys/fs/cgroup/"


class CGroupProcessListAPIView(GenericAPIView):
    """Lists tasks pids by cgroup. Raises 404 if cgroup does not exist. Cgroup_name should be urlencoded."""

    queryset = None
    serializer_class = None

    def get(self, request, *args, **kwargs):
        path = os.path.join(cgroup_path_prefix, unquote(kwargs["cgroup_name"]), "tasks")
        print(path)
        if not os.path.exists(path):
            raise NotFound()

        with open(path) as f:
            return Response(f.read().splitlines())
