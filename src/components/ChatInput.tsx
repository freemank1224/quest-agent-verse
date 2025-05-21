
import React, { useState, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Mic, Send, Volume2, VolumeX } from "lucide-react";
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
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex flex-col w-full gap-3">
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入您的问题..."
          className="min-h-[60px] resize-none bg-white/80"
          disabled={isGenerating}
        />
        
        <div className="flex justify-between items-center">
          <div className="flex space-x-2">
            <Button 
              type="button" 
              variant="outline" 
              size="sm"
              onClick={handleMicClick}
              disabled={isGenerating}
              className="flex items-center gap-1"
            >
              <Mic className="h-4 w-4" /> 
              <span>使用语音输入</span>
            </Button>
            
            <Button 
              type="button" 
              variant={isSpeakerOn ? "default" : "outline"} 
              size="sm"
              onClick={onSpeakerToggle}
              className="flex items-center gap-1"
            >
              {isSpeakerOn ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
              <span>{isSpeakerOn ? '关闭朗读' : '开启朗读'}</span>
            </Button>
          </div>
          
          <Button type="submit" disabled={!input.trim() || isGenerating}>
            {isGenerating ? '正在生成...' : '发送'}
            {!isGenerating && <Send className="ml-2 h-4 w-4" />}
          </Button>
        </div>
      </div>
    </form>
  );
};

export default ChatInput;
