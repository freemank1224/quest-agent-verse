
import React, { createContext, useState, useContext, ReactNode } from 'react';

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
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
