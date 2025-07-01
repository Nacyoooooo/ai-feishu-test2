from api.cluster_api import ClusterAPI

cluster_api = ClusterAPI()


class ClusterCommon:

    def __init__(self):
        self.xxx = 'xxx'

    def create_cluster(self, cluster_name, vpc_id):
        instance_types = cluster_api.get_available_instance_types(region="guangzhou")
        instance_type = instance_types[0]
        data = {
            "region": "guangzhou",
            "instance_type": instance_type,
            "cluster_name": cluster_name,
            "vpc_id": vpc_id
        }
        return cluster_api.create_cluster(data)
