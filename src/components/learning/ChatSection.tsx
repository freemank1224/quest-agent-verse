
import React, { useRef, useEffect } from 'react';
import ChatBubble from '@/components/ChatBubble';
import { MessageType } from '@/contexts/ChatContext';

interface ChatSectionProps {
  messages: MessageType[];
  userAvatar: string;
  agentAvatar: string;
}

const ChatSection: React.FC<ChatSectionProps> = ({ 
  messages, 
  userAvatar, 
  agentAvatar 
}) => {
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll to the bottom when messages change
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div 
      ref={chatContainerRef}
      className="flex-grow overflow-y-auto px-4 py-6 space-y-4 bg-gray-50"
    >
      {messages.map((message) => (
        <ChatBubble 
          key={message.id} 
          message={message} 
          avatar={message.sender === 'user' ? userAvatar : agentAvatar} 
        />
      ))}
    </div>
  );
};

export default ChatSection;
