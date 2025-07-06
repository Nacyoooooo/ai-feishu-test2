from api.base_api import APIClient
import logging


class ListMessageAPI(APIClient):
    def __init__(self, access_token):
        self.access_token = access_token
        super().__init__()
    def list_messages(self, container_id_type, container_id, start_time=None, end_time=None, 
                     sort_type="ByCreateTimeAsc", page_size=20, page_token=None):
        """获取会话历史消息
        
        Args:
            container_id_type: 容器类型，chat(单聊/群聊)或thread(话题)
            container_id: 容器ID，与container_id_type对应
            start_time: 起始时间戳(秒级)，可选
            end_time: 结束时间戳(秒级)，可选
            sort_type: 排序方式，ByCreateTimeAsc(升序)或ByCreateTimeDesc(降序)
            page_size: 分页大小，1-50，默认20
            page_token: 分页标记，第一次请求不填
            
        Returns:
            响应结果，包含消息列表和分页信息
        """
        endpoint = "/open-apis/im/v1/messages"
        params = {
            "container_id_type": container_id_type,
            "container_id": container_id,
            "sort_type": sort_type,
            "page_size": page_size
        }
        
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if page_token:
            params["page_token"] = page_token
            
        logging.info(f"Requesting messages with params: {params}")
        return self.get(endpoint, params=params)