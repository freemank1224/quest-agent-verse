import React, { useState } from 'react';
import { MessageType } from '@/contexts/ChatContext';
import { cn } from '@/lib/utils';
import MarkdownRenderer from './MarkdownRenderer';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronRight, Brain } from 'lucide-react';

interface ChatBubbleProps {
  message: MessageType;
  avatar?: string;
}

// 解析消息内容，分离思考内容和实际回复
const parseMessageContent = (content: string) => {
  // 匹配 <think>...</think> 或 <thinking>...</thinking> 标签
  const thinkRegex = /<think(?:ing)?>([\s\S]*?)<\/think(?:ing)?>/gi;
  
  let thinkingContent = '';
  let actualContent = content;
  
  // 提取思考内容
  const thinkMatches = content.match(thinkRegex);
  if (thinkMatches) {
    thinkingContent = thinkMatches.map(match => {
      // 移除标签，保留内容
      return match.replace(/<\/?think(?:ing)?>/gi, '').trim();
    }).join('\n\n');
    
    // 从实际内容中移除思考部分
    actualContent = content.replace(thinkRegex, '').trim();
  }
  
  return {
    thinkingContent,
    actualContent: actualContent || content // 如果没有实际内容，使用原始内容
  };
};

const ChatBubble: React.FC<ChatBubbleProps> = ({ message, avatar }) => {
  const { content, sender } = message;
  const [showThinking, setShowThinking] = useState(false);
  
  // 解析消息内容
  const { thinkingContent, actualContent } = parseMessageContent(content);
  const hasThinking = thinkingContent.length > 0 && sender === 'agent';
  
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
        {/* 思考内容展开/收起按钮 */}
        {hasThinking && (
          <div className="mb-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowThinking(!showThinking)}
              className="text-xs h-6 px-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50"
            >
              <Brain className="w-3 h-3 mr-1" />
              思考过程
              {showThinking ? (
                <ChevronDown className="w-3 h-3 ml-1" />
              ) : (
                <ChevronRight className="w-3 h-3 ml-1" />
              )}
            </Button>
          </div>
        )}
        
        {/* 思考内容（可展开） */}
        {hasThinking && showThinking && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg border-l-4 border-blue-300">
            <div className="text-xs text-gray-600 mb-2 font-medium flex items-center">
              <Brain className="w-3 h-3 mr-1" />
              AI思考过程
            </div>
            <div className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
              {thinkingContent}
            </div>
          </div>
        )}
        
        {/* 实际回复内容 */}
        {sender === 'user' ? (
          <p className="whitespace-pre-wrap">{actualContent}</p>
        ) : (
          <MarkdownRenderer content={actualContent} />
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
