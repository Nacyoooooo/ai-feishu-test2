import pytest
from test_data.user_test_data import TestData

@pytest.mark.api
class TestAPICases:
    def test_get_products(self, common_api):
        """测试获取产品列表接口"""
        endpoint = TestData.get_api_endpoints()['products']
        response = common_api.get_user_api().get(endpoint)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0

    @pytest.mark.smoke
    def test_create_user_with_valid_data(self, common_api):
        """测试使用有效数据创建用户接口"""
        endpoint = TestData.get_api_endpoints()['users']
        user_data = TestData.get_valid_user()
        response = common_api.get_user_api().create_user(user_data)
        
        assert response.status_code == 201
        assert response.json()['username'] == user_data['username']
        assert response.json()['email'] == user_data['email']

    def test_create_user_with_invalid_data(self, common_api):
        """测试使用无效数据创建用户接口"""
        endpoint = TestData.get_api_endpoints()['users']
        invalid_data = TestData.get_invalid_user()
        response = common_api.get_user_api().create_user(invalid_data)
        
        assert response.status_code in [400, 422]

    def test_cleanup_test_data(self, common_api, clean_test_data):
        """测试测试数据清理功能"""
        # 这里可以添加验证清理逻辑的代码
        pass