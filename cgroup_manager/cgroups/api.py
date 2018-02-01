import os
from subprocess import CalledProcessError, check_call
from urllib.parse import unquote

from cgroup_manager.cgroups.serializers import CgroupCreateSerializer, CgroupProcessAddSerializer
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

cgroup_path_prefix = "/sys/fs/cgroup/"


class CGroupProcessListAddAPIView(GenericAPIView):
    """Lists tasks pids by cgroup. Raises 404 if cgroup does not exist. cgroup_path_fragment should be urlencoded."""

    queryset = None

    def get(self, request, *args, **kwargs):
        path = os.path.join(cgroup_path_prefix, unquote(kwargs["cgroup_path_fragment"]), "tasks")
        if not os.path.exists(path):
            raise NotFound()

        with open(path) as f:
            return Response(f.read().splitlines())

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        pid = serializer.validated_data["pid"]
        path = os.path.join(cgroup_path_prefix, unquote(kwargs["cgroup_path_fragment"]), "tasks")
        try:
            check_call(["echo", pid, ">", path])
        except CalledProcessError:
            # on purpose. The error should not show command used as this might be a security risk
            raise ValidationError(
                detail={"errors": ["Adding process to cgroup failed. Please check hierarchy and cgroup name."]})

        return Response(serializer.data, status=HTTP_200_OK)

    def get_serializer_class(self):
        # otherwise swagger complains
        if self.request.method == "PUT":
            return CgroupProcessAddSerializer


class CgroupCreateAPIView(GenericAPIView):
    """Create cgroup in given hierarchy"""

    queryset = None
    serializer_class = CgroupCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        hierarchy = unquote(kwargs["hierarchy"])
        cgroup_path_fragment = unquote(serializer.validated_data['cgroup_path_fragment'])
        path = os.path.join(cgroup_path_prefix, hierarchy, cgroup_path_fragment)
        try:
            check_call(["mkdir", "-p", path])
        except CalledProcessError:
            # on purpose. The error should not show command used as this might be a security risk
            raise ValidationError(
                detail={"errors": ["Creating cgroup returned an error. Please check hierarchy and cgroup name."]})
        return Response(serializer.data, status=HTTP_201_CREATED)
