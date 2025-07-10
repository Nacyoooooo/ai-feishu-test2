from api.base_api import APIClient
import os


class UploadFileAPI(APIClient):
    def __init__(self, access_token):
        self.access_token = access_token
        super().__init__()

    def upload_file(self, file_type, file_name, file_path):
        """上传文件到飞书
        Args:
            file_type: 文件类型，如mp4
            file_name: 文件名
            file_path: 本地文件路径
        Returns:
            响应结果
        """
        endpoint = f"/open-apis/im/v1/files"
        
        # 构造multipart/form-data数据
        files = {
            'file_type': (None, file_type),
            'file_name': (None, file_name),
            'file': (file_path, open(file_path, 'rb'))
        }
        
        # 临时移除Content-Type，让requests自动处理
        original_headers = self.session.headers.copy()
        if 'Content-Type' in self.session.headers:
            del self.session.headers['Content-Type']
        
        try:
            response = self.post(endpoint, files=files)
        finally:
            # 恢复原始headers
            self.session.headers.update(original_headers)
            # 关闭文件
            files['file'][1].close()
        
        return response