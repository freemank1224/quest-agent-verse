#!/usr/bin/env python3
"""
测试 WebSocket 连接和 TeacherAgent 响应
"""
import asyncio
import websockets
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """测试 WebSocket 连接和消息处理"""
    uri = "ws://localhost:8000/api/ws/chat/test_client_123"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"成功连接到 WebSocket: {uri}")
            
            # 发送测试消息
            test_message = {
                "content": "你好，我想学习Python编程，请问可以给我一些建议吗？",
                "sender": "user"
            }
            
            logger.info(f"发送消息: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # 等待响应
            logger.info("等待 TeacherAgent 响应...")
            response = await websocket.recv()
            response_data = json.loads(response)
            
            logger.info("收到响应:")
            logger.info(f"Content: {response_data.get('content', 'No content')[:100]}...")
            logger.info(f"Sender: {response_data.get('sender', 'Unknown')}")
            logger.info(f"ID: {response_data.get('id', 'No ID')}")
            
            # 发送第二条消息测试连续对话
            test_message2 = {
                "content": "我是初学者，请问从哪里开始学习比较好？",
                "sender": "user"
            }
            
            logger.info(f"发送第二条消息: {test_message2}")
            await websocket.send(json.dumps(test_message2))
            
            # 等待第二个响应
            response2 = await websocket.recv()
            response_data2 = json.loads(response2)
            
            logger.info("收到第二个响应:")
            logger.info(f"Content: {response_data2.get('content', 'No content')[:100]}...")
            logger.info(f"Sender: {response_data2.get('sender', 'Unknown')}")
            
            logger.info("WebSocket 测试完成！")
            
    except Exception as e:
        logger.error(f"WebSocket 连接失败: {e}")
        return False
    
    return True

async def main():
    """主函数"""
    logger.info("开始测试 WebSocket 连接...")
    
    success = await test_websocket_connection()
    
    if success:
        logger.info("✅ WebSocket 连接测试成功！")
    else:
        logger.error("❌ WebSocket 连接测试失败！")

if __name__ == "__main__":
    asyncio.run(main())
