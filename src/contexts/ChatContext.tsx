import React, { createContext, useState, useContext, ReactNode, useEffect, useRef } from 'react';
import { connectWebSocket } from '@/services/api';

// Define types for messages
export type MessageType = {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: Date;
};

// Define types for the chat context
type ChatContextType = {
  messages: MessageType[];
  addMessage: (content: string, sender: 'user' | 'agent') => void;
  clearMessages: () => void;
  initialPrompt: string;
  setInitialPrompt: (prompt: string) => void;
  isGenerating: boolean;
  setIsGenerating: (isGenerating: boolean) => void;
  sendMessage: (content: string) => void;
  clientId: string;
};

// Create context with a default value
const ChatContext = createContext<ChatContextType | undefined>(undefined);

// Hook to use the chat context
export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

// 生成或获取持久化的客户端ID
const getClientId = () => {
  let clientId = localStorage.getItem('client_id');
  if (!clientId) {
    clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('client_id', clientId);
  }
  return clientId;
};

// Provider component
export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [initialPrompt, setInitialPrompt] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [clientId] = useState<string>(getClientId()); // 使用持久化的客户端ID
  const socketRef = useRef<any>(null);

  useEffect(() => {
    console.log('Initializing WebSocket connection with client ID:', clientId);
    
    // 初始化WebSocket连接
    socketRef.current = connectWebSocket(
      clientId,
      (data) => {
        // 处理收到的消息
        console.log('Received message from WebSocket:', data);
        addMessage(data.content, data.sender);
        setIsGenerating(false);
      },
      () => {
        console.log('WebSocket connection closed');
        setIsGenerating(false);
      }
    );

    // 组件卸载时关闭WebSocket连接
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [clientId]);

  // Add a new message to the chat
  const addMessage = (content: string, sender: 'user' | 'agent') => {
    const newMessage: MessageType = {
      id: Date.now().toString(),
      content,
      sender,
      timestamp: new Date(),
    };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
  };

  // Send a message through WebSocket
  const sendMessage = (content: string) => {
    if (socketRef.current) {
      console.log('Sending message:', content, 'from client:', clientId);
      
      // 先显示用户消息
      addMessage(content, 'user');
      
      // 设置正在生成响应状态
      setIsGenerating(true);
      
      // 发送消息到服务器
      socketRef.current.send(content, 'user');
    } else {
      console.error('WebSocket connection not available');
      setIsGenerating(false);
    }
  };

  // Clear all messages
  const clearMessages = () => {
    setMessages([]);
  };

  // Context value
  const value = {
    messages,
    addMessage,
    clearMessages,
    initialPrompt,
    setInitialPrompt,
    isGenerating,
    setIsGenerating,
    sendMessage,
    clientId, // 暴露clientId给组件使用
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
