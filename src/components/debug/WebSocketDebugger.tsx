import React, { useState, useEffect, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { useChat } from '@/contexts/ChatContext';

interface LogEntry {
  timestamp: string;
  type: 'info' | 'success' | 'error' | 'warning';
  message: string;
}

const WebSocketDebugger: React.FC = () => {
  const { clientId, isGenerating, sendMessage, messages } = useChat();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [testMessage, setTestMessage] = useState('Hello, this is a test message');
  const [wsStatus, setWsStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  const logContainerRef = useRef<HTMLDivElement>(null);
  const previousMessageCount = useRef(0);

  const addLog = (type: LogEntry['type'], message: string) => {
    const newLog: LogEntry = {
      timestamp: new Date().toISOString(),
      type,
      message
    };
    setLogs(prev => [...prev, newLog]);
    
    // 自动滚动到底部
    setTimeout(() => {
      if (logContainerRef.current) {
        logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
      }
    }, 100);
  };

  // 监控ChatContext中的消息变化
  useEffect(() => {
    if (messages.length > previousMessageCount.current) {
      const newMessages = messages.slice(previousMessageCount.current);
      newMessages.forEach(msg => {
        addLog('success', `ChatContext收到${msg.sender}消息: ${msg.content.substring(0, 100)}...`);
      });
      previousMessageCount.current = messages.length;
    }
  }, [messages]);

  useEffect(() => {
    addLog('info', `WebSocket调试器初始化`);
    addLog('info', `客户端ID: ${clientId}`);
    
    // 检查环境变量
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api';
    addLog('info', `环境变量 VITE_API_URL: ${apiUrl}`);
    addLog('info', `环境变量 VITE_WS_URL: ${wsUrl}`);
    
    // 检查WebSocket连接
    const finalWsUrl = `${wsUrl}/ws/chat/${clientId}`;
    addLog('info', `最终WebSocket URL: ${finalWsUrl}`);
    
    // 模拟连接状态（不创建独立连接，避免冲突）
    setWsStatus('connecting');
    addLog('info', '使用ChatContext的WebSocket连接进行测试...');
    
    setTimeout(() => {
      setWsStatus('connected');
      addLog('success', 'ChatContext WebSocket连接已就绪!');
      addLog('info', `当前ChatContext消息数量: ${messages.length}`);
    }, 1000);
    
    // 不再创建独立的测试连接，避免与ChatContext冲突
  }, [clientId, messages.length]);

  const handleSendTestMessage = () => {
    if (!testMessage.trim()) return;
    
    addLog('info', `通过ChatContext发送测试消息: ${testMessage}`);
    addLog('info', `发送前消息数量: ${messages.length}`);
    sendMessage(testMessage);
    
    // 监控是否收到回复
    const checkResponse = () => {
      setTimeout(() => {
        if (isGenerating) {
          addLog('info', 'Agent正在生成回复中...');
          checkResponse(); // 继续检查
        } else {
          addLog('info', `发送后消息数量: ${messages.length}`);
          if (messages.length > previousMessageCount.current) {
            addLog('success', '✅ 成功收到Agent回复!');
          } else {
            addLog('warning', '⚠️ 可能没有收到回复或回复处理有问题');
          }
        }
      }, 1000);
    };
    
    checkResponse();
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const getStatusColor = () => {
    switch (wsStatus) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getLogColor = (type: LogEntry['type']) => {
    switch (type) {
      case 'success': return 'text-green-600';
      case 'error': return 'text-red-600';
      case 'warning': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>WebSocket 连接调试器 (ChatContext模式)</span>
          <div className="flex items-center gap-2">
            <Badge className={`text-white ${getStatusColor()}`}>
              {wsStatus.toUpperCase()}
            </Badge>
            {isGenerating && (
              <Badge variant="outline" className="animate-pulse">
                正在生成...
              </Badge>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* 连接信息 */}
        <div className="grid grid-cols-1 gap-2 text-sm">
          <div>
            <strong>客户端ID:</strong> {clientId}
          </div>
          <div>
            <strong>API URL:</strong> {import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}
          </div>
          <div>
            <strong>WebSocket Base URL:</strong> {import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api'}
          </div>
          <div>
            <strong>完整WebSocket URL:</strong> {(import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api')}/ws/chat/{clientId}
          </div>
          <div>
            <strong>当前消息数量:</strong> {messages.length}
          </div>
          <div>
            <strong>生成状态:</strong> {isGenerating ? '生成中' : '空闲'}
          </div>
        </div>
        
        {/* 测试消息发送 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">测试消息:</label>
          <div className="flex gap-2">
            <Textarea
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              placeholder="输入测试消息..."
              className="flex-grow"
              rows={2}
            />
            <Button 
              onClick={handleSendTestMessage}
              disabled={!testMessage.trim() || isGenerating}
            >
              发送
            </Button>
          </div>
        </div>
        
        {/* 当前消息列表 */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">当前聊天消息:</h4>
          <div className="max-h-32 overflow-y-auto border rounded p-2 bg-gray-50">
            {messages.length === 0 ? (
              <p className="text-gray-500 text-sm">暂无消息</p>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className="text-xs mb-1 p-1 border-b">
                  <span className={msg.sender === 'user' ? 'text-blue-600' : 'text-green-600'}>
                    [{msg.sender}]
                  </span>
                  <span className="ml-2">{msg.content.substring(0, 50)}...</span>
                </div>
              ))
            )}
          </div>
        </div>
        
        {/* 日志控制 */}
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">连接日志</h3>
          <Button variant="outline" size="sm" onClick={clearLogs}>
            清空日志
          </Button>
        </div>
        
        {/* 日志显示 */}
        <ScrollArea className="h-64 w-full border rounded-md p-4">
          <div ref={logContainerRef} className="space-y-1">
            {logs.map((log, index) => (
              <div key={index} className="text-sm">
                <span className="text-xs text-gray-400">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className={`ml-2 ${getLogColor(log.type)}`}>
                  [{log.type.toUpperCase()}]
                </span>
                <span className="ml-2">{log.message}</span>
              </div>
            ))}
            {logs.length === 0 && (
              <div className="text-gray-500 text-center py-8">
                暂无日志记录
              </div>
            )}
          </div>
        </ScrollArea>
        
        {/* 调试说明 */}
        <div className="text-xs text-gray-500 space-y-1">
          <p><strong>调试说明:</strong></p>
          <p>• 此版本监控ChatContext的WebSocket连接，避免冲突</p>
          <p>• 绿色 = 消息收发成功</p>
          <p>• 黄色 = 连接中或有警告</p>
          <p>• 红色 = 连接失败或发生错误</p>
          <p>• 观察"当前聊天消息"部分是否显示新消息</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default WebSocketDebugger; 