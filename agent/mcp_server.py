import logging
from fastmcp import FastMCP
from common.robot_common import get_app_access_token
from api.message.send_message_api import SendMessageAPI

from urllib.parse import urlparse, urlunparse, quote
import json
import logging
import os
import uuid
from typing import AsyncGenerator

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
# 配置详细日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

mcp = FastMCP(name="MCP Server")

# @mcp.tool()
# def add(a:int,b:int)->int:
#     """计算两数之和"""
#     result = a + b
#     log.info(f"add a={a},b={b},result={result}")
#     return result

app_id = 'cli_a8ee0c6a92e7501c'
app_secret = '9kbasiKxCyonOjJ2BCfXHcaKLKPA4fJT'
open_id = 'ou_adf4e416e22c12c5d4b40e347315f68c'

@mcp.tool(name="发送消息",description="发送消息，并返回消息id")
def send_message():
    """测试前置：创建群聊，并返回群聊ID"""
    log.info('发送消息')
    token = get_app_access_token(app_id, app_secret)
    send_message_api = SendMessageAPI(token)
    resp=send_message_api.send_message(open_id, {"text":"123"})
    return resp['data']['message_id']
import yaml
import os

from test_data import read_data_from_yaml

@mcp.tool(name="config",description="获取配置文件信息")
def get_config():
    """获取配置文件信息"""
    robots=read_data_from_yaml('robots.yaml','robots')
    receivers=read_data_from_yaml('robots.yaml','receivers')
    return {
        "robots":robots,
        "receivers":receivers
    }



@mcp.tool(name="获取飞书API的json格式化文档",description="获取飞书API的json格式化文档")
def fetch_json_data(url: str) -> dict:
    log.info(f'格式化文档{url}')
    def transform_url(original_url):
        parsed = urlparse(original_url)
        clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

        doc_index = clean_url.find('/document/')
        if doc_index == -1:
            raise ValueError("URL中未找到/document/路径")

        path_after_document = clean_url[doc_index + len('/document'):]
        encoded_path = quote(path_after_document, safe='')

        new_url = f"https://open.feishu.cn/document_portal/v1/document/get_detail?fullPath={encoded_path}"
        return new_url
    new_url=transform_url(url)
    """从URL获取JSON数据"""
    try:
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
        response = requests.get(new_url, headers=headers)
        response.raise_for_status()
        return response.json()['data']['schema']['apiSchema']['responses']
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取数据失败: {str(e)}")
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)