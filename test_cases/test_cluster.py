import logging
import os

import pytest

from api.cluster_api import ClusterAPI
from common.cluster_common import ClusterCommon
from test_data import read_data_from_yaml


class TestCluster:
    """集群相关测试用例"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.cluster_api = ClusterAPI()
        cls.cluster_common = ClusterCommon()

    @pytest.mark.P0
    @pytest.mark.parametrize("cluster_data", read_data_from_yaml(
        "cluster_case.yaml",
        "create_cluster"
    ))
    def test_create_cluster(self, cluster_data):
        """测试创建集群"""
        resp = self.cluster_common.create_cluster(cluster_data["cluster_name"], cluster_data["vpc_id"])
        assert resp["code"] == cluster_data["code"], \
            logging.info(f"和预期结果不对应，预期结果：{cluster_data['code']}，实际结果：{resp['code']}")
    
    @pytest.mark.P0
    @pytest.mark.parametrize("cluster_data", read_data_from_yaml(
        "cluster_case.yaml",
        "rename_cluster"
    ))
    def test_rename_cluster(self, cluster_data):
        """测试修改集群名字"""
        resp = self.cluster_api.rename_cluster(cluster_data['cluster_name'])
        assert resp["code"] == cluster_data["code"], \
            logging.info(f"和预期结果不对应，预期结果：{cluster_data['code']}，实际结果：{resp['code']}")


if __name__ == '__main__':
    pytest.main(["-m", "P0", __file__])