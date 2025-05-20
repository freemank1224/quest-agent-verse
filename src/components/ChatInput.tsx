
import React, { useState, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Mic, Send } from "lucide-react";
import { useChat } from '@/contexts/ChatContext';
import { sendQueryToAgent } from '@/services/api';
import { toast } from "@/components/ui/sonner";

interface ChatInputProps {
  onSpeakerToggle?: () => void;
  isSpeakerOn?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSpeakerToggle, isSpeakerOn }) => {
  const [input, setInput] = useState('');
  const { addMessage, setIsGenerating, isGenerating } = useChat();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isGenerating) return;

    // Add user message
    addMessage(input, 'user');
    setInput('');
    setIsGenerating(true);

    try {
      // Send message to API
      const response = await sendQueryToAgent(input);
      // Add agent response
      addMessage(response, 'agent');
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('发送消息失败，请重试');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleMicClick = () => {
    toast.info('语音输入功能即将推出');
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col w-full gap-2">
      <div className="flex items-center gap-2">
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入您的问题..."
          className="min-h-[60px] resize-none"
          disabled={isGenerating}
        />
      </div>
      <div className="flex justify-between">
        <Button 
          type="button" 
          variant="outline" 
          size="icon" 
          onClick={handleMicClick}
          disabled={isGenerating}
        >
          <Mic className="h-4 w-4" />
        </Button>
        <Button type="submit" disabled={!input.trim() || isGenerating}>
          {isGenerating ? '正在生成...' : '发送'}
          {!isGenerating && <Send className="ml-2 h-4 w-4" />}
        </Button>
      </div>
    </form>
  );
};

export default ChatInput;
