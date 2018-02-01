from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import os
from rest_framework.exceptions import NotFound, ValidationError
from urllib.parse import unquote
from cgroup_manager.cgroups.serializers import CgroupCreateSerializer
from subprocess import check_call, CalledProcessError
from rest_framework.status import HTTP_201_CREATED

cgroup_path_prefix = "/sys/fs/cgroup/"


class CGroupProcessListAPIView(GenericAPIView):
    """Lists tasks pids by cgroup. Raises 404 if cgroup does not exist. Cgroup_name should be urlencoded."""

    queryset = None
    serializer_class = None

    def get(self, request, *args, **kwargs):
        path = os.path.join(cgroup_path_prefix, unquote(kwargs["cgroup_name"]), "tasks")
        if not os.path.exists(path):
            raise NotFound()

        with open(path) as f:
            return Response(f.read().splitlines())


class CgroupCreateAPIView(GenericAPIView):
    """Create cgroup in given hierarchy"""

    queryset = None
    serializer_class = CgroupCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        hierarchy = unquote(kwargs["hierarchy"])
        cgroup_name = unquote(serializer.validated_data['cgroup_name'])
        path = os.path.join(cgroup_path_prefix, hierarchy, cgroup_name)
        try:
            check_call(["mkdir", "-p", path])
        except CalledProcessError:
            # on purpose. The error should not show command used as this might be a security risk
            raise ValidationError(
                detail={"errors": ["Creating cgroup returned an error. Please check hierarchy and cgroup name."]})
        return Response(serializer.data, status=HTTP_201_CREATED)
