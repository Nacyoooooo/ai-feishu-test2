from api.user_api import UserAPI

class CommonAPI:
    """公共API封装类，整合多个业务API"""
    def __init__(self, base_url):
        self.user_api = UserAPI(base_url)
        # 可添加更多业务API实例
        # self.product_api = ProductAPI(base_url)
        # self.order_api = OrderAPI(base_url)

    def get_user_api(self):
        """获取用户业务API实例"""
        return self.user_api

    # 可添加更多业务API的获取方法
    # def get_product_api(self):
    #     return self.product_api