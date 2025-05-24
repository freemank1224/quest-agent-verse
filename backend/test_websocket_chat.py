#!/usr/bin/env python3
"""
WebSocket聊天功能测试

模拟前端发送消息，测试是否能正常接收到Agent回复
"""

import asyncio
import websockets
import json
import time
import uuid
from datetime import datetime

async def test_websocket_chat():
    """测试WebSocket聊天功能"""
    print("🔗 WebSocket聊天功能测试")
    print("=" * 50)
    
    # 生成测试客户端ID
    client_id = f"test_client_{int(time.time())}"
    ws_url = f"ws://localhost:8000/api/ws/chat/{client_id}"
    
    print(f"客户端ID: {client_id}")
    print(f"连接URL: {ws_url}")
    
    try:
        # 连接WebSocket
        print("\n📡 尝试连接WebSocket...")
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket连接成功!")
            
            # 测试消息列表
            test_messages = [
                "你好，我想学习小学数学加法",
                "什么是2+3？",
                "请详细解释一下加法运算的原理"
            ]
            
            for i, message in enumerate(test_messages, 1):
                print(f"\n--- 测试消息 {i} ---")
                print(f"发送消息: {message}")
                
                # 发送消息
                message_data = {
                    "content": message,
                    "sender": "user"
                }
                
                await websocket.send(json.dumps(message_data))
                print("✅ 消息已发送")
                
                # 等待回复
                print("⏳ 等待Agent回复...")
                start_time = time.time()
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=300.0)  # 5分钟超时
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    print(f"✅ 收到回复! 耗时: {duration:.2f}秒")
                    
                    # 解析回复
                    response_data = json.loads(response)
                    
                    print(f"回复内容预览: {response_data.get('content', 'N/A')[:100]}...")
                    print(f"发送者: {response_data.get('sender', 'N/A')}")
                    print(f"时间戳: {response_data.get('timestamp', 'N/A')}")
                    
                    # 检查是否有错误
                    if response_data.get('error'):
                        print("❌ 回复中包含错误信息!")
                        return False
                    
                    # 检查回复是否为空
                    content = response_data.get('content', '')
                    if not content or content.strip() == '':
                        print("❌ 回复内容为空!")
                        return False
                    
                    print("✅ 回复格式正确且包含内容")
                    
                    # 每个消息之间间隔一下
                    if i < len(test_messages):
                        print("⏱️  等待2秒后发送下一条消息...")
                        await asyncio.sleep(2)
                        
                except asyncio.TimeoutError:
                    print("❌ 等待回复超时!")
                    return False
                except Exception as e:
                    print(f"❌ 处理回复时出错: {e}")
                    return False
            
            print(f"\n🎉 所有测试消息都成功收到回复!")
            return True
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket连接被关闭: {e}")
        return False
    except ConnectionRefusedError:
        print("❌ 无法连接到WebSocket服务器，请确保后端服务正在运行")
        print("启动命令: cd backend && python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ WebSocket连接错误: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_connection():
    """测试简单的WebSocket连接"""
    print("\n🔍 测试简单WebSocket连接...")
    
    client_id = f"simple_test_{int(time.time())}"
    ws_url = f"ws://localhost:8000/api/ws/chat/{client_id}"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket连接建立成功")
            
            # 发送一个简单消息
            simple_message = {"content": "Hello", "sender": "user"}
            await websocket.send(json.dumps(simple_message))
            print("✅ 简单消息发送成功")
            
            # 等待回复
            response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
            print("✅ 收到回复")
            
            response_data = json.loads(response)
            print(f"回复内容: {response_data.get('content', 'N/A')[:50]}...")
            
            return True
            
    except Exception as e:
        print(f"❌ 简单连接测试失败: {e}")
        return False

def check_backend_status():
    """检查后端服务状态"""
    print("🔍 检查后端服务状态...")
    
    import requests
    
    try:
        # 检查API根路径
        response = requests.get("http://localhost:8000/api", timeout=5)
        if response.status_code == 200 or response.status_code == 404:  # 404也表示服务在运行
            print("✅ 后端API服务正在运行")
            return True
        else:
            print(f"⚠️  后端API响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("请确保后端服务已启动:")
        print("cd backend && python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ 检查后端状态时出错: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 WebSocket聊天功能综合测试")
    print("测试前端无法接收到Agent回复的问题")
    print("=" * 60)
    
    # 1. 检查后端服务状态
    if not check_backend_status():
        print("\n❌ 后端服务未运行，请先启动后端服务")
        return
    
    # 2. 测试简单连接
    print("\n" + "="*60)
    simple_success = await test_simple_connection()
    
    if not simple_success:
        print("❌ 简单连接测试失败，WebSocket服务可能有问题")
        return
    
    # 3. 测试完整聊天功能
    print("\n" + "="*60)
    chat_success = await test_websocket_chat()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试结果总结:")
    print(f"  简单连接测试: {'✅ 通过' if simple_success else '❌ 失败'}")
    print(f"  聊天功能测试: {'✅ 通过' if chat_success else '❌ 失败'}")
    
    if simple_success and chat_success:
        print("\n🎉 所有测试通过! WebSocket聊天功能正常")
        print("\n💡 如果前端仍然无法接收回复，请检查:")
        print("1. 前端WebSocket连接URL是否正确")
        print("2. 前端消息处理逻辑是否正确")
        print("3. 浏览器开发者工具中的网络和控制台日志")
    else:
        print("\n❌ 测试失败，WebSocket聊天功能存在问题")
        print("\n🔍 可能的问题:")
        print("1. Agent处理消息时出现异常")
        print("2. 模型推理超时或失败")
        print("3. WebSocket连接处理有问题")
        print("4. 后端依赖服务(如Ollama)未正常运行")

if __name__ == "__main__":
    asyncio.run(main()) 