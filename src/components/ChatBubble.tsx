
import React from 'react';
import { MessageType } from '@/contexts/ChatContext';
import { cn } from '@/lib/utils';
import MarkdownRenderer from './MarkdownRenderer';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

interface ChatBubbleProps {
  message: MessageType;
  avatar?: string;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ message, avatar }) => {
  const { content, sender } = message;
  
  // Get initials for avatar fallback
  const getInitials = () => {
    return sender === 'user' ? 'U' : 'AI';
  };
  
  return (
    <div className={cn(
      "flex mb-4 items-start",
      sender === 'user' ? "justify-end" : "justify-start"
    )}>
      {sender !== 'user' && (
        <Avatar className="mr-2 flex-shrink-0">
          <AvatarImage src={avatar} alt="Agent" />
          <AvatarFallback>{getInitials()}</AvatarFallback>
        </Avatar>
      )}
      
      <div
        className={cn(
          "chat-bubble",
          sender === 'user' 
            ? "chat-bubble-user" 
            : "chat-bubble-agent"
        )}
      >
        {sender === 'user' ? (
          <p className="whitespace-pre-wrap">{content}</p>
        ) : (
          <MarkdownRenderer content={content} />
        )}
        <div className="text-xs opacity-50 text-right mt-1">
          {new Date(message.timestamp).toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit'
          })}
        </div>
      </div>
      
      {sender === 'user' && (
        <Avatar className="ml-2 flex-shrink-0">
          <AvatarImage src={avatar} alt="User" />
          <AvatarFallback>{getInitials()}</AvatarFallback>
        </Avatar>
      )}
    </div>
  );
};

export default ChatBubble;
