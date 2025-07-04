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
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

os.environ['OPENAI_API_KEY'] = 'sk-9ef6e0e5b0db4da580331750f5de8997'
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_API_KEY'] = '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'

llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    streaming=True  # 启用流式响应
)

app = FastAPI(title="AI代码生成API", description="基于飞书文档生成API代码和测试用例")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class CodeGenerationRequest(BaseModel):
    url: str = None
    json_data: str = None
    template: str = None

DEFAULT_TEMPLATE = """
根据下面的json数据的$.schema.apiSchema.responses，检索出以下内容：请求路径、请求参数、请求体、响应体以及响应体中的不同code，帮我生成代码，json数据如下：

{json_data}

代码规范和示例如下，请严格遵守，并确保覆盖所有的错误码，如果有不能够覆盖的错误码，请在生成完代码后告知我这些错误码以及对应的场景，示例代码中调用的函数默认已被实现，不要有多余的代码：
API接口：
    def send_message(self, receive_id, content, receive_id_type, msg_type="text", uuid=None):
    \"\"\"发送飞书消息
    Args:
        receive_id: 接收者ID
        content: 消息内容字典，如{{"text":"消息文本"}}
        msg_type: 消息类型，默认为text
        uuid: 消息唯一标识，选填
        receive_id_type: 接收者ID类型，可选值: user_id, open_id, union_id, email, chat_id
    Returns:
        响应结果
    \"\"\"
    endpoint = f"/im/v1/messages?receive_id_type={{receive_id_type}}"
    data = {{
        "content": json.dumps(content),
        "msg_type": msg_type,
        "receive_id": receive_id,
        "uuid": uuid
    }}
    return self.post(endpoint, data)
测试用例：
    @pytest.mark.P0
    @pytest.mark.parametrize('send_message_data', read_data_from_yaml(
        "message_case.yaml",
        "send_message"
    ))
    def test_send_message(self, send_message_data):
        \"\"\"测试发送消息API，增加详细日志和错误处理\"\"\"
        message_api = SendMessageAPI()
        receive_id = send_message_data['receive_id']
        receive_type = send_message_data['receive_id_type']

        resp = message_api.send_message(receive_id=receive_id, receive_id_type=receive_type,
                                            content=send_message_data['content'],
                                            msg_type="text")
        assert resp["code"] == send_message_data["expected_code"], \
            logging.info(f"和预期结果不对应，预期结果：{{send_message_data['expected_code']}}，实际结果：{{resp['code']}}")    
测试用例参数：
    send_message:
        - content: {{"text": ""}}
          expected_code: 230001
          receive_id: "ou_adf4e416e22c12c5d4b40e347315f68c"
          receive_id_type: "open_id"
        - content: {{"text": "Hello World2"}}
          expected_code: 0
          receive_id: "ou_adf4e416e22c12c5d4b40e347315f68c"
          receive_id_type: "open_id"
"""

generation_tasks = {}

async def fetch_json_data(url: str) -> dict:
    """从URL获取JSON数据"""
    try:
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取数据失败: {str(e)}")

async def generate_code_stream(json_data: str, template: str = None) -> AsyncGenerator[str, None]:
    """流式生成代码"""
    if template is None:
        template = DEFAULT_TEMPLATE
    
    prompt = PromptTemplate.from_template(template)
    filled_prompt = prompt.format(json_data=json_data)
    
    try:
        async for chunk in llm.astream(filled_prompt):
            if chunk.content:
                # EventSourceResponse会自动添加data:前缀和\n\n
                yield chunk.content

        # 发送结束标记
        yield "[DONE]"
    except Exception as e:
        logger.error(f"生成代码时发生错误: {str(e)}")
        yield f"生成代码时发生错误: {str(e)}"
        yield "[DONE]"

@app.get("/")
async def root():
    """根路径 - 返回Web界面"""
    return FileResponse("static/index.html")

@app.get("/api")
async def api_info():
    """API信息"""
    return {"message": "AI代码生成API服务正在运行", "version": "1.0.0"}

@app.post("/generate-code")
async def generate_code_stream_endpoint(request: CodeGenerationRequest):
    """生成代码的流式接口"""
    from urllib.parse import urlparse, urlunparse, quote

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
    try:
        # 获取JSON数据
        if request.url:
            new_request_url = transform_url(request.url)
            json_data = await fetch_json_data(new_request_url)
            json_str = json.dumps(json_data, ensure_ascii=False)
            logger.info(f"飞书API文档json数据：{json_str}")
        elif request.json_data:
            json_str = request.json_data
        else:
            raise HTTPException(status_code=400, detail="必须提供url或json_data")
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        logger.info(f"创建新任务: {task_id}")
        
        # 存储任务信息
        generation_tasks[task_id] = {
            'json_data': json_str,
            'template': request.template,
            'status': 'pending'
        }
        
        logger.info(f"任务 {task_id} 已创建，状态: pending")
        return {"task_id": task_id, "status": "started"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate-code-stream")
async def generate_code_stream_endpoint_get(task_id: str = None):
    """EventSource流式接口"""
    logger.info(f"收到EventSource连接请求，任务ID: {task_id}")
    
    if not task_id or task_id not in generation_tasks:
        logger.error(f"无效的任务ID: {task_id}")
        raise HTTPException(status_code=400, detail="无效的任务ID")
    
    task = generation_tasks[task_id]
    task['status'] = 'running'
    logger.info(f"任务 {task_id} 状态更新为: running")
    
    try:
        logger.info(f"开始为任务 {task_id} 生成流式响应")
        return EventSourceResponse(
            generate_code_stream(task['json_data'], task['template']),
            media_type="text/event-stream"
        )
    except Exception as e:
        task['status'] = 'error'
        logger.error(f"任务 {task_id} 发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 清理任务
        if task_id in generation_tasks:
            del generation_tasks[task_id]
            logger.info(f"任务 {task_id} 已清理")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "AI代码生成API"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

