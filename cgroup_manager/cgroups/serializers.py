from cgroup_manager.cgroups.utils import check_if_process_exists
from rest_framework import serializers


class CgroupCreateSerializer(serializers.Serializer):
    cgroup_path_fragment = serializers.CharField(max_length=255)


class CgroupProcessAddSerializer(serializers.Serializer):
    pid = serializers.IntegerField(max_value=32768, min_value=1)

    def validate_pid(self, value):
        if not check_if_process_exists(value):
            raise serializers.ValidationError("Process does not exist.")
        return value
