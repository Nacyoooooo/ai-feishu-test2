from api.base_api import APIClient


class EmployeeAPI(APIClient):
    def create_employee(self, employee_id_type, name, mobile):
        """创建员工
        Args:
            employee_id_type: 员工id类型
            name: 员工姓名
            mobile: 员工手机号
        Returns:
            响应结果
        """
        endpoint = f"/directory/v1/employees?employee_id_type={employee_id_type}"
        data = {
            "employee": {
                "name": {
                    "name": {
                        "default_value": name
                    }
                },
                "mobile": mobile
            }
        }
        return self.post(endpoint, data)


