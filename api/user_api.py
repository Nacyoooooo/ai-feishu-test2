from api.base_api import APIClient

class UserAPI(APIClient):
    """用户业务API类，封装用户相关接口"""
    def get_user_info(self, user_id):
        """获取用户信息"""
        return self.get(f"users/{user_id}")

    def create_user(self, user_data):
        """创建新用户"""
        return self.post("users", json=user_data)

    def update_user(self, user_id, user_data):
        """更新用户信息"""
        return self.put(f"users/{user_id}", json=user_data)

    def delete_user(self, user_id):
        """删除用户"""
        return self.delete(f"users/{user_id}")