import React, { createContext, useState, useContext, ReactNode, useEffect, useRef, useCallback } from 'react';
import { connectWebSocket } from '@/services/api';

// Define types for messages
export type MessageType = {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: Date;
};

// Define types for user background information
export type UserBackgroundType = {
  age: string;
  learningGoal: string;
  timePreference: string;
  knowledgeLevel?: string;
  targetAudience?: string;
  specialRequirements?: string[];
};

// Define types for the formatted prompt that will be sent to agents
export type FormattedPromptType = {
  originalPrompt: string;
  userBackground: UserBackgroundType;
  formattedPrompt: string;
  timestamp: Date;
};

// Define types for the chat context
type ChatContextType = {
  messages: MessageType[];
  addMessage: (content: string, sender: 'user' | 'agent') => void;
  clearMessages: () => void;
  initialPrompt: string;
  setInitialPrompt: (prompt: string) => void;
  userBackground: UserBackgroundType | null;
  setUserBackground: (background: UserBackgroundType) => void;
  formattedPrompt: FormattedPromptType | null;
  createFormattedPrompt: (originalPrompt: string, background: UserBackgroundType) => FormattedPromptType;
  isGenerating: boolean;
  setIsGenerating: (isGenerating: boolean) => void;
  sendMessage: (content: string, background?: UserBackgroundType) => void;
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
  const [userBackground, setUserBackground] = useState<UserBackgroundType | null>(null);
  const [formattedPrompt, setFormattedPrompt] = useState<FormattedPromptType | null>(null);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [clientId] = useState<string>(getClientId()); // 使用持久化的客户端ID
  const socketRef = useRef<any>(null);

  // Create formatted prompt for agents
  const createFormattedPrompt = useCallback((originalPrompt: string, background: UserBackgroundType): FormattedPromptType => {
    // 创建结构化的提示词，将背景信息作为独立参数
    const formatted: FormattedPromptType = {
      originalPrompt,
      userBackground: background,
      formattedPrompt: `${originalPrompt}

## 用户背景信息
年龄/年级: ${background.age}
学习目标: ${background.learningGoal}
时间偏好: ${background.timePreference}
${background.knowledgeLevel ? `知识水平: ${background.knowledgeLevel}` : ''}
${background.targetAudience ? `目标受众: ${background.targetAudience}` : ''}
${background.specialRequirements?.length ? `特殊要求: ${background.specialRequirements.join(', ')}` : ''}

## Agent处理指令
请所有后续Agent (CoursePlanner, ContentGenerator, Monitor, Verifier等) 在处理时考虑以上背景信息：
1. 根据年龄/年级调整内容难度和教学方法
2. 对齐学习目标，确保课程设计符合用户期望
3. 考虑时间约束，合理安排学习进度和内容密度
4. 在内容验证和监督过程中应用这些背景信息作为评估标准`,
      timestamp: new Date()
    };
    
    setFormattedPrompt(formatted);
    return formatted;
  }, []);

  // Add a new message to the chat - 使用 useCallback 避免闭包问题
  const addMessage = useCallback((content: string, sender: 'user' | 'agent') => {
    console.log('Adding message to chat:', { content: content.substring(0, 50) + '...', sender });
    const newMessage: MessageType = {
      id: Date.now().toString(),
      content,
      sender,
      timestamp: new Date(),
    };
    setMessages((prevMessages) => {
      console.log('Current messages count:', prevMessages.length);
      const updatedMessages = [...prevMessages, newMessage];
      console.log('Updated messages count:', updatedMessages.length);
      return updatedMessages;
    });
  }, []);

  // Send a message through WebSocket with optional background information
  const sendMessage = useCallback((content: string, background?: UserBackgroundType) => {
    if (socketRef.current) {
      let messageToSend = content;
      
      // 如果提供了背景信息，创建格式化的提示词
      if (background) {
        const formatted = createFormattedPrompt(content, background);
        messageToSend = formatted.formattedPrompt;
        console.log('Sending formatted message with background:', {
          original: content,
          background,
          formatted: messageToSend.substring(0, 100) + '...'
        });
      } else if (formattedPrompt) {
        // 如果之前已经设置了格式化提示词，继续使用
        messageToSend = `${content}

## 继续使用之前的用户背景信息
${JSON.stringify(formattedPrompt.userBackground, null, 2)}`;
      }
      
      console.log('Sending message:', messageToSend.substring(0, 100) + '...', 'from client:', clientId);
      
      // 先显示用户原始消息（不显示格式化后的长消息）
      addMessage(content, 'user');
      
      // 设置正在生成响应状态
      setIsGenerating(true);
      
      // 发送格式化的消息到服务器
      socketRef.current.send(messageToSend, 'user');
    } else {
      console.error('WebSocket connection not available');
      setIsGenerating(false);
    }
  }, [clientId, addMessage, createFormattedPrompt, formattedPrompt]);

  // Clear all messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  useEffect(() => {
    console.log('Initializing WebSocket connection with client ID:', clientId);
    
    // 初始化WebSocket连接
    socketRef.current = connectWebSocket(
      clientId,
      (data) => {
        // 处理收到的消息
        console.log('Received message from WebSocket:', data);
        console.log('Message content length:', data.content?.length);
        console.log('Message sender:', data.sender);
        
        // 确保收到的是agent消息且有内容
        if (data.sender === 'agent' && data.content) {
          console.log('Processing agent message...');
          addMessage(data.content, data.sender);
          setIsGenerating(false);
        } else {
          console.warn('Received invalid message format:', data);
          setIsGenerating(false);
        }
      },
      () => {
        console.log('WebSocket connection closed');
        setIsGenerating(false);
      }
    );

    // 组件卸载时关闭WebSocket连接
    return () => {
      if (socketRef.current) {
        console.log('Closing WebSocket connection');
        socketRef.current.close();
      }
    };
  }, [clientId, addMessage]);

  // Context value
  const value = {
    messages,
    addMessage,
    clearMessages,
    initialPrompt,
    setInitialPrompt,
    userBackground,
    setUserBackground,
    formattedPrompt,
    createFormattedPrompt,
    isGenerating,
    setIsGenerating,
    sendMessage,
    clientId, // 暴露clientId给组件使用
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
