
import React from 'react';
import { MessageType } from '@/contexts/ChatContext';
import { cn } from '@/lib/utils';
import MarkdownRenderer from './MarkdownRenderer';

interface ChatBubbleProps {
  message: MessageType;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ message }) => {
  const { content, sender } = message;
  
  return (
    <div className={cn(
      "flex mb-4",
      sender === 'user' ? "justify-end" : "justify-start"
    )}>
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
    </div>
  );
};

export default ChatBubble;
