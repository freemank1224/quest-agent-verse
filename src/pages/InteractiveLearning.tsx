
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import Navbar from '@/components/Navbar';
import { useChat } from '@/contexts/ChatContext';
import { getUserProgress } from '@/services/api';
import { toast } from '@/components/ui/sonner';
import { useAuth } from '@/contexts/AuthContext';

// Import the new components
import LearningProgress from '@/components/learning/LearningProgress';
import ImagePanel from '@/components/learning/ImagePanel';
import ChatSection from '@/components/learning/ChatSection';
import ChatInputPanel from '@/components/learning/ChatInputPanel';

const InteractiveLearning = () => {
  const navigate = useNavigate();
  const { messages, initialPrompt, addMessage } = useChat();
  const { user, profile } = useAuth();
  const [userProgress, setUserProgress] = useState<any>(null);
  const [isLoadingProgress, setIsLoadingProgress] = useState(true);
  const [isSpeakerOn, setIsSpeakerOn] = useState(false);
  const [currentImageUrl, setCurrentImageUrl] = useState('https://source.unsplash.com/random/800x400/?education');
  const [isImagePanelOpen, setIsImagePanelOpen] = useState(true);

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

  const toggleSpeaker = () => {
    setIsSpeakerOn(!isSpeakerOn);
    toast.info(isSpeakerOn ? '已关闭文本朗读' : '已开启文本朗读');
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
              
              <LearningProgress 
                userProgress={userProgress}
                isLoadingProgress={isLoadingProgress}
                user={user}
              />
            </div>
          </ResizablePanel>
          
          <ResizableHandle withHandle />
          
          {/* Right panel - Chat interface */}
          <ResizablePanel defaultSize={75}>
            <div className="relative h-[calc(100vh-4rem)] flex flex-col">
              {/* Top floating panel - Image display with water drop shaped toggle button */}
              <ImagePanel 
                isImagePanelOpen={isImagePanelOpen}
                setIsImagePanelOpen={setIsImagePanelOpen}
                imageUrl={currentImageUrl}
              />
              
              {/* Main chat area */}
              <ChatSection 
                messages={messages}
                userAvatar={userAvatar}
                agentAvatar={agentAvatar}
              />
              
              {/* Bottom floating panel - Chat input with frosted glass effect */}
              <ChatInputPanel 
                onSpeakerToggle={toggleSpeaker}
                isSpeakerOn={isSpeakerOn}
              />
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
};

export default InteractiveLearning;
