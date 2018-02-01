from rest_framework import serializers


class CgroupCreateSerializer(serializers.Serializer):
    cgroup_path_fragment = serializers.CharField(max_length=255)
