#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试流式响应内容
"""

import json
import io
from config.settings import get_config
from services.dify_client import DifyClient
from services.file_service import FileService

def test_stream_details():
    """测试流式响应的详细内容"""
    print("=== 详细测试流式响应内容 ===")
    
    # 检查配置
    config = get_config('development')
    if not config.DIFY_API_BASE_URL or not config.DIFY_API_TOKEN:
        print("错误: DIFY_API_BASE_URL 或 DIFY_API_TOKEN 未配置")
        return
    
    print(f"使用配置: DIFY_API_BASE_URL={config.DIFY_API_BASE_URL}")
    print(f"使用配置: DIFY_API_TOKEN={config.DIFY_API_TOKEN[:10]}...")
    
    # 创建测试文件
    test_content = "这是一个测试文件，用于审查系统的功能测试。\n包含一些测试内容。"
    test_file = io.BytesIO(test_content.encode('utf-8'))
    test_file.name = 'test_file.txt'
    
    # 模拟FileStorage对象
    from werkzeug.datastructures import FileStorage
    file_storage = FileStorage(
        stream=test_file,
        filename='test_file.txt',
        content_type='text/plain'
    )
    
    # 上传文件
    dify_client = DifyClient(config.DIFY_API_TOKEN, config.DIFY_API_BASE_URL)
    file_id = dify_client.upload_file(file_storage, "test_user")
    print(f"文件上传成功，文件ID: {file_id}")
    
    # 创建文件输入
    file_storage.stream.seek(0)  # 重置文件指针
    file_input = FileService.create_dify_file_input(file_storage, file_id)
    
    # 准备聊天输入
    chat_inputs = {
        'file': file_input,
        'Category': '政策'
    }
    
    print(f"聊天输入: {json.dumps(chat_inputs, ensure_ascii=False)}")
    print("\n--- 开始详细分析流式响应 ---")
    
    # 流式聊天
    response_count = 0
    node_finished_events = []
    all_events = []
    
    try:
        for chunk in dify_client.chat_stream(chat_inputs, "test_user"):
            if chunk.strip():
                response_count += 1
                
                # 尝试解析JSON
                try:
                    if chunk.startswith('data: '):
                        json_str = chunk[6:].strip()
                        if json_str:
                            data = json.loads(json_str)
                            event_type = data.get('event', 'unknown')
                            all_events.append(data)
                            
                            if event_type == 'node_finished':
                                node_finished_events.append(data)
                                node_data = data.get('data', {})
                                title = node_data.get('title', 'Unknown')
                                status = node_data.get('status', 'unknown')
                                outputs = node_data.get('outputs', {})
                                
                                print(f"响应块 {response_count}: node_finished - {title} ({status})")
                                
                                # 检查是否包含答案
                                if outputs and 'answer' in outputs:
                                    answer = outputs['answer']
                                    print(f"  答案内容: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                                
                                # 检查是否是前端期望的节点
                                if title in ['直接回复 2', '直接回复2', '直接回复 3', '直接回复3']:
                                    print(f"  *** 这是前端期望的节点: {title} ***")
                            elif event_type == 'message':
                                answer = data.get('answer', '')
                                if answer:
                                    print(f"响应块 {response_count}: message - {answer[:50]}{'...' if len(answer) > 50 else ''}")
                            elif event_type in ['workflow_started', 'workflow_finished']:
                                print(f"响应块 {response_count}: {event_type}")
                            
                except json.JSONDecodeError as e:
                    print(f"响应块 {response_count}: JSON解析失败: {e}")
                except Exception as e:
                    print(f"响应块 {response_count}: 数据处理失败: {e}")
                    
    except Exception as e:
        print(f"流式聊天错误: {e}")
    finally:
        dify_client.close()
    
    print(f"\n=== 总结 ===")
    print(f"总共接收到 {response_count} 个响应块")
    print(f"发现 {len(node_finished_events)} 个 node_finished 事件")
    
    print("\n所有 node_finished 事件的节点标题:")
    for i, event in enumerate(node_finished_events):
        node_data = event.get('data', {})
        title = node_data.get('title', 'Unknown')
        status = node_data.get('status', 'unknown')
        outputs = node_data.get('outputs', {})
        has_answer = 'answer' in outputs if outputs else False
        print(f"  {i+1}. {title} (状态: {status}, 有答案: {has_answer})")
    
    # 查找所有包含"直接回复"的节点
    direct_reply_nodes = [event for event in node_finished_events 
                         if '直接回复' in event.get('data', {}).get('title', '')]
    
    print(f"\n包含'直接回复'的节点 ({len(direct_reply_nodes)} 个):")
    for i, event in enumerate(direct_reply_nodes):
        node_data = event.get('data', {})
        title = node_data.get('title', 'Unknown')
        outputs = node_data.get('outputs', {})
        if outputs and 'answer' in outputs:
            answer = outputs['answer']
            print(f"  {i+1}. {title}: {answer[:200]}{'...' if len(answer) > 200 else ''}")

if __name__ == "__main__":
    test_stream_details()