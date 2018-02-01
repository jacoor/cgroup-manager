from rest_framework import serializers


class CgroupCreateSerializer(serializers.Serializer):
    cgroup_name = serializers.CharField(max_length=255)
