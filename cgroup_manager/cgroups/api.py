from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import os
from rest_framework.exceptions import NotFound


cgroup_path_prefix = "/sys/fs/cgroup/"


class CGroupProcessListAPIView(GenericAPIView):
    queryset = None
    serializer_class = None

    def get(self, request, *args, **kwargs):
        if not os.path.exists(kwargs["cgroup_name"]):
            raise NotFound()

        with open(os.path.join(cgroup_path_prefix, kwargs["cgroup_name"], "tasks")) as f:
            return Response(f.read().splitlines())
