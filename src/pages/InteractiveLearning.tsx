import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { ChevronDown, ChevronUp } from "lucide-react";
import Navbar from '@/components/Navbar';
import ChatInput from '@/components/ChatInput';
import ChatBubble from '@/components/ChatBubble';
import LoadingPlaceholder from '@/components/LoadingPlaceholder';
import { useChat } from '@/contexts/ChatContext';
import { getUserProgress } from '@/services/api';
import { toast } from '@/components/ui/sonner';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '@/contexts/AuthContext';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

const InteractiveLearning = () => {
  const navigate = useNavigate();
  const { messages, initialPrompt, addMessage } = useChat();
  const { user, profile } = useAuth();
  const [userProgress, setUserProgress] = useState<any>(null);
  const [isLoadingProgress, setIsLoadingProgress] = useState(true);
  const [isSpeakerOn, setIsSpeakerOn] = useState(false);
  const [currentImageUrl, setCurrentImageUrl] = useState('https://source.unsplash.com/random/800x400/?education');
  const [isImagePanelOpen, setIsImagePanelOpen] = useState(true);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!initialPrompt) {
      toast.error('请先输入您想学习的内容');
      navigate('/');
    }
  }, [initialPrompt, navigate]);

  useEffect(() => {
    const fetchUserProgress = async () => {
      try {
        setIsLoadingProgress(true);
        const data = await getUserProgress();
        setUserProgress(data);
      } catch (error) {
        console.error('Error fetching user progress:', error);
      } finally {
        setIsLoadingProgress(false);
      }
    };

    fetchUserProgress();

    // Add a welcome message if there are no messages
    if (messages.length === 0 && initialPrompt) {
      const welcomeMessage = `欢迎来到"${initialPrompt}"的互动学习！我是您的AI学习助手，可以帮助您回答问题、解释概念、提供练习题等。请问有什么我可以帮助您的？`;
      addMessage(welcomeMessage, 'agent');
    }
  }, []);

  useEffect(() => {
    // Scroll to the bottom when messages change
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const toggleSpeaker = () => {
    setIsSpeakerOn(!isSpeakerOn);
    toast.info(isSpeakerOn ? '已关闭文本朗读' : '已开启文本朗读');
  };

  const toggleImagePanel = () => {
    setIsImagePanelOpen(!isImagePanelOpen);
  };

  // User avatar - using profile.avatar_url if available or fallback
  const userAvatar = profile?.avatar_url || 'https://source.unsplash.com/random/100x100/?portrait';
  const agentAvatar = 'https://source.unsplash.com/random/100x100/?robot';

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      
      <div className="flex-grow flex">
        <ResizablePanelGroup direction="horizontal">
          {/* Left sidebar - Learning resources */}
          <ResizablePanel defaultSize={25} minSize={20} maxSize={40}>
            <div className="h-[calc(100vh-4rem)] p-4 overflow-y-auto bg-white border-r border-gray-200">
              <h2 className="text-xl font-bold mb-4 font-display">学习资源</h2>
              
              {isLoadingProgress ? (
                <div className="space-y-6">
                  <LoadingPlaceholder />
                  <LoadingPlaceholder lines={5} />
                </div>
              ) : userProgress ? (
                <div className="space-y-6">
                  {/* Course progress */}
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                    <h3 className="font-medium text-gray-900 mb-2">学习进度</h3>
                    <Progress value={userProgress.progressPercentage} className="h-2 mb-2" />
                    <p className="text-sm text-gray-600">已完成 {userProgress.progressPercentage}%</p>
                  </div>
                  
                  {/* Achievements */}
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                    <h3 className="font-medium text-gray-900 mb-2">成就列表</h3>
                    <ul className="space-y-2">
                      {userProgress.achievements.map((achievement: any) => (
                        <li key={achievement.id} className="flex items-center">
                          <span className="h-2 w-2 bg-green-500 rounded-full mr-2"></span>
                          <div>
                            <p className="text-sm font-medium">{achievement.title}</p>
                            <p className="text-xs text-gray-600">{achievement.description}</p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Knowledge graph placeholder */}
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                    <h3 className="font-medium text-gray-900 mb-2">知识图谱</h3>
                    <div className="text-sm text-gray-600">
                      这里将显示与您的学习相关的知识图谱，帮助您理解概念间的关联。
                    </div>
                    <div className="mt-2 h-32 bg-gray-100 rounded flex items-center justify-center border border-gray-200">
                      <p className="text-gray-500 text-sm">知识图谱预览区域</p>
                    </div>
                  </div>
                  
                  {!user && (
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                      <h3 className="font-medium text-gray-900 mb-2">保存您的进度</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        创建一个账户以保存您的学习进度并获得个性化推荐。
                      </p>
                      <Button 
                        onClick={() => navigate('/auth')} 
                        size="sm" 
                        className="w-full"
                      >
                        登录 / 注册
                      </Button>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500">无法加载学习资源</p>
              )}
            </div>
          </ResizablePanel>
          
          <ResizableHandle withHandle />
          
          {/* Right panel - Chat interface */}
          <ResizablePanel defaultSize={75}>
            <div className="relative h-[calc(100vh-4rem)] flex flex-col">
              {/* Top floating panel - Image display with water drop shaped toggle button */}
              <Collapsible
                open={isImagePanelOpen}
                onOpenChange={setIsImagePanelOpen}
                className="w-full"
              >
                <div className="sticky top-0 z-10 backdrop-blur-lg bg-white/60 shadow-sm border-b border-gray-200">
                  <CollapsibleContent>
                    <div className="p-3">
                      <div className="aspect-[2/1] bg-gray-50 rounded-lg overflow-hidden border border-gray-100">
                        <img
                          src={currentImageUrl}
                          alt="学习相关图片"
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </div>
                  </CollapsibleContent>
                  <div className="flex justify-end">
                    <CollapsibleTrigger asChild>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="absolute bottom-0 right-4 transform translate-y-1/2 rounded-full w-10 h-10 p-0 bg-white shadow-md hover:bg-gray-100 border border-gray-100 flex items-center justify-center"
                        style={{
                          boxShadow: '0 4px 10px rgba(0, 0, 0, 0.08)',
                          zIndex: 20
                        }}
                      >
                        {isImagePanelOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </Button>
                    </CollapsibleTrigger>
                  </div>
                </div>
              </Collapsible>
              
              {/* Main chat area */}
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
              
              {/* Bottom floating panel - Chat input with frosted glass effect */}
              <div className="sticky bottom-4 z-10 mx-4">
                <div className="backdrop-blur-md bg-white/70 rounded-lg shadow-md p-4 border border-gray-100">
                  <ChatInput 
                    onSpeakerToggle={toggleSpeaker}
                    isSpeakerOn={isSpeakerOn}
                  />
                </div>
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
};

export default InteractiveLearning;
