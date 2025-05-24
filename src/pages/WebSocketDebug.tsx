import React from 'react';
import Navbar from '@/components/Navbar';
import WebSocketDebugger from '@/components/debug/WebSocketDebugger';
import { ChatProvider } from '@/contexts/ChatContext';

const WebSocketDebug: React.FC = () => {
  return (
    <ChatProvider>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              WebSocket 连接调试
            </h1>
            <p className="text-gray-600">
              用于诊断前端WebSocket连接问题和消息收发状态
            </p>
          </div>
          
          <WebSocketDebugger />
          
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">
              调试流程说明
            </h3>
            <div className="space-y-2 text-sm text-blue-800">
              <p><strong>1. 连接测试：</strong>页面加载时会自动尝试建立WebSocket连接</p>
              <p><strong>2. 消息测试：</strong>连接成功后会自动发送一条测试消息</p>
              <p><strong>3. 手动测试：</strong>可以在输入框中输入自定义消息进行测试</p>
              <p><strong>4. 日志查看：</strong>所有连接状态和消息收发都会记录在日志中</p>
            </div>
            
            <div className="mt-4 space-y-2 text-sm text-blue-800">
              <p><strong>预期结果：</strong></p>
              <p>• 如果WebSocket连接正常：状态显示为"CONNECTED"，日志中会出现"收到回复"记录</p>
              <p>• 如果连接失败：状态显示为"ERROR"，日志中会显示具体错误信息</p>
              <p>• 如果能收到回复：说明前后端通信正常，问题可能在InteractiveLearning页面的特定逻辑中</p>
            </div>
          </div>
        </div>
      </div>
    </ChatProvider>
  );
};

export default WebSocketDebug; 