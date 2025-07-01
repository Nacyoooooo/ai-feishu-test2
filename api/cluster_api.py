from api.base_api import APIClient

class ClusterAPI(APIClient):

    def get_available_instance_types(self, region="beijing"):
        """获取可用套餐"""
        data = {
            'region': region,
        }
        return self.post("/cluster/instance-types", data)

    def create_cluster(self, data):
        """创建集群（这种请求体比较复杂的，可以直接在common里面写好请求体然后传过来，
        而且请求体里面的有些参数是可以写死的，不需要通过测试用例的参数来传）"""
        return self.post("/cluster/create", data)

    def rename_cluster(self, new_cluster_name):
        """修改集群名字"""
        data = {
            'cluster_name': new_cluster_name,
        }
        return self.post("/cluster/rename", data)