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

from ai_service import ai_service

logger = logging.getLogger(__name__)

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
    streaming: bool = True  # 新增参数，控制是否使用流式响应

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
        return response.json()['data']['schema']['apiSchema']['responses']
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取数据失败: {str(e)}")

@app.get("/")
async def root():
    """根路径 - 返回Web界面"""
    return FileResponse("static/index.html")

@app.get("/api")
async def api_info():
    """API信息"""
    return {"message": "AI代码生成API服务正在运行", "version": "1.0.0"}

@app.post("/generate-code")
async def generate_code_endpoint(request: CodeGenerationRequest):
    """生成代码的接口，支持流式和非流式两种模式"""
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
        if request.url:
            new_request_url = transform_url(request.url)
            json_data = await fetch_json_data(new_request_url)
            json_str = json.dumps(json_data, ensure_ascii=False)
            logger.info(f"飞书API文档json数据：{json_str}")
        elif request.json_data:
            json_str = request.json_data
        else:
            raise HTTPException(status_code=400, detail="必须提供url或json_data")
        
        # 如果请求流式响应，创建任务并返回任务ID
        if request.streaming:
            task_id = str(uuid.uuid4())
            logger.info(f"创建新流式任务: {task_id}")
            
            generation_tasks[task_id] = {
                'json_data': json_str,
                'template': request.template,
                'status': 'pending'
            }
            
            logger.info(f"任务 {task_id} 已创建，状态: pending")
            return {"task_id": task_id, "status": "started", "streaming": True}
        else:
            # 非流式响应，直接生成代码
            logger.info("开始非流式代码生成")
            try:
                result = await ai_service.generate_code_non_streaming(json_str, request.template)
                logger.info("非流式代码生成完成")
                return {"code": result, "status": "completed", "streaming": False}
            except Exception as e:
                logger.error(f"非流式代码生成失败: {str(e)}")
                raise HTTPException(status_code=500, detail=f"代码生成失败: {str(e)}")
    
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
            ai_service.generate_code_stream(task['json_data'], task['template']),
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

@app.post("/generate-code-sync")
async def generate_code_sync_endpoint(request: CodeGenerationRequest):
    """同步生成代码接口（非流式）"""
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
        if request.url:
            new_request_url = transform_url(request.url)
            json_data = await fetch_json_data(new_request_url)
            json_str = json.dumps(json_data, ensure_ascii=False)
            logger.info(f"飞书API文档json数据：{json_str}")
        elif request.json_data:
            json_str = request.json_data
        else:
            raise HTTPException(status_code=400, detail="必须提供url或json_data")
        
        # 直接生成代码
        logger.info("开始同步代码生成")
        try:
            result = await ai_service.generate_code_non_streaming(json_str, request.template)
            logger.info("同步代码生成完成")
            return {"code": result, "status": "completed"}
        except Exception as e:
            logger.error(f"同步代码生成失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"代码生成失败: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

