import React, { createContext, useState, useContext, ReactNode, useEffect, useRef } from 'react';
import { connectWebSocket } from '@/services/api';
import { v4 as uuidv4 } from 'uuid';

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

// Provider component
export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [initialPrompt, setInitialPrompt] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [clientId] = useState<string>(uuidv4());
  const socketRef = useRef<any>(null);

  useEffect(() => {
    // 初始化WebSocket连接
    socketRef.current = connectWebSocket(
      clientId,
      (data) => {
        // 处理收到的消息
        addMessage(data.content, data.sender);
        setIsGenerating(false);
      },
      () => {
        console.log('WebSocket connection closed');
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
      // 先显示用户消息
      addMessage(content, 'user');
      
      // 设置正在生成响应状态
      setIsGenerating(true);
      
      // 发送消息到服务器
      socketRef.current.send(content, 'user');
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
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
