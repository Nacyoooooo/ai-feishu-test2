class TestData:
    @staticmethod
    def get_valid_user():
        """返回有效的用户数据"""
        return {
            "username": "test_user",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }

    @staticmethod
    def get_invalid_user():
        """返回无效的用户数据"""
        return {
            "username": "",
            "email": "invalid-email",
            "password": "123"
        }

    @staticmethod
    def get_test_products():
        """返回测试产品列表"""
        return [
            {"id": 1, "name": "Product A", "price": 99.99},
            {"id": 2, "name": "Product B", "price": 199.99}
        ]

    @staticmethod
    def get_api_endpoints():
        """返回API端点配置"""
        return {
            "users": "/api/v1/users",
            "products": "/api/v1/products",
            "auth": "/api/v1/auth"
        }