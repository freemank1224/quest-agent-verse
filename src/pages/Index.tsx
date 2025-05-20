
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useChat } from '@/contexts/ChatContext';
import { useAuth } from '@/contexts/AuthContext';
import Navbar from '@/components/Navbar';

const Index = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const navigate = useNavigate();
  const { setInitialPrompt } = useChat();
  const { user } = useAuth();

  const handleSubmit = () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    setInitialPrompt(prompt);
    
    // Simulate API call
    setTimeout(() => {
      setIsGenerating(false);
      navigate('/course-planning');
    }, 2000);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      
      <main className="flex-grow flex items-center justify-center">
        <div className="max-w-3xl w-full px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl font-display">
              智能学习助手
            </h1>
            <p className="mt-4 text-xl text-gray-600">
              个性化学习体验，AI 支持的教育平台
            </p>
          </div>
          
          <div className="bg-white shadow-lg rounded-xl p-8 max-w-2xl mx-auto border border-gray-200">
            <h2 className="text-2xl font-bold mb-6 text-center font-display">今天你想了解什么？</h2>
            
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="例如：我想学习高中物理中的力学知识..."
              className="min-h-[120px] mb-6 bg-gray-50 border border-gray-200"
            />
            
            <div className="flex justify-center">
              <Button 
                onClick={handleSubmit} 
                disabled={!prompt.trim() || isGenerating}
                size="lg"
                className={`gradient-bg font-medium transition-all duration-300 animate-flow-right ${
                  isGenerating ? 'opacity-90' : 'hover:shadow-lg'
                }`}
              >
                {isGenerating ? '正在生成...' : '去探索'}
              </Button>
            </div>
            
            {!user && (
              <div className="mt-8 pt-6 border-t border-gray-200">
                <p className="text-center text-gray-600 mb-4">创建账户以保存您的学习进度和个性化推荐</p>
                <div className="flex justify-center space-x-4">
                  <Button 
                    variant="outline" 
                    onClick={() => navigate('/auth')}
                  >
                    登录
                  </Button>
                  <Button 
                    onClick={() => navigate('/auth')}
                  >
                    注册账户
                  </Button>
                </div>
              </div>
            )}
          </div>
          
          <div className="mt-12 text-center">
            <p className="text-gray-600">
              开启您的个性化学习之旅，获得量身定制的课程内容
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
