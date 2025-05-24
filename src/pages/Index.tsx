
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useChat } from '@/contexts/ChatContext';
import { useAuth } from '@/contexts/AuthContext';
import Navbar from '@/components/Navbar';
import { X, ChevronRight } from 'lucide-react';
import type { UserBackgroundType } from '@/contexts/ChatContext';

const Index = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [showQuestionModal, setShowQuestionModal] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [userAge, setUserAge] = useState('');
  const [learningGoal, setLearningGoal] = useState('');
  const [timePreference, setTimePreference] = useState('');
  const navigate = useNavigate();
  const { setInitialPrompt, setUserBackground, createFormattedPrompt, sendMessage } = useChat();
  const { user } = useAuth();

  const handleSubmit = () => {
    if (!prompt.trim()) return;
    
    // 显示问题弹窗来收集背景信息
    setShowQuestionModal(true);
  };

  const handleQuestionNext = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    } else {
      // 最后一步，准备生成课程
      handleFinalSubmit();
    }
  };

  const handleFinalSubmit = () => {
    setIsGenerating(true);
    setShowQuestionModal(false);
    
    // 创建结构化的用户背景信息
    const backgroundInfo: UserBackgroundType = {
      age: userAge,
      learningGoal: learningGoal,
      timePreference: timePreference,
      // 可以根据输入推断的额外信息
      knowledgeLevel: inferKnowledgeLevel(userAge),
      targetAudience: userAge,
    };
    
    // 设置背景信息到Context
    setUserBackground(backgroundInfo);
    
    // 创建格式化的提示词
    const formattedPrompt = createFormattedPrompt(prompt, backgroundInfo);
    
    // 设置初始提示词（用于页面显示）
    setInitialPrompt(prompt);
    
    console.log('用户背景信息:', backgroundInfo);
    console.log('格式化提示词:', formattedPrompt);
    
    // 发送带背景信息的消息到后端
    sendMessage(prompt, backgroundInfo);
    
    // 导航到课程规划页面
    setTimeout(() => {
      setIsGenerating(false);
      navigate('/course-planning');
    }, 1000);
  };

  // 根据年龄推断知识水平的辅助函数
  const inferKnowledgeLevel = (age: string): string => {
    if (age.includes('小学生')) return '基础入门';
    if (age.includes('初中生')) return '初级进阶';
    if (age.includes('高中生')) return '中级进阶';
    if (age.includes('大学生')) return '高级进阶';
    if (age.includes('成年人')) return '专业发展';
    return '待评估';
  };

  const handleCloseModal = () => {
    setShowQuestionModal(false);
    setCurrentStep(1);
    setUserAge('');
    setLearningGoal('');
    setTimePreference('');
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 1: return userAge.trim() !== '';
      case 2: return learningGoal.trim() !== '';
      case 3: return timePreference.trim() !== '';
      default: return false;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 curved-lines-bg">
      {/* 曲线流动背景 */}
      <div className="curved-lines-container">
        <div className="curved-line"></div>
        <div className="curved-line"></div>
        <div className="curved-line"></div>
        <div className="curved-line"></div>
        <div className="curved-line"></div>
        <div className="curved-line"></div>
        <div className="curved-line"></div>
        <div className="curved-line"></div>
      </div>
      
      <Navbar />
      
      <main className="flex-grow flex items-center justify-center z-10 relative">
        <div className="max-w-3xl w-full px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl font-display">
              智能学习助手
            </h1>
            <p className="mt-4 text-xl text-gray-600">
              个性化学习体验，AI 支持的教育平台
            </p>
          </div>
          
          <div className="glass-effect shadow-lg rounded-xl p-8 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold mb-6 text-center font-display">今天你想了解什么？</h2>
            
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="例如：我想学习高中物理中的力学知识..."
              className="min-h-[120px] mb-6 bg-gray-50/80 border border-gray-200"
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

      {/* 悬浮问题弹窗 - 毛玻璃效果 */}
      {showQuestionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 modal-overlay">
          {/* 背景遮罩 */}
          <div 
            className="absolute inset-0 bg-black/20 backdrop-blur-sm"
            onClick={handleCloseModal}
          />
          
          {/* 弹窗内容 */}
          <div className="relative w-full max-w-md mx-auto modal-content">
            <div className="glass-modal border border-white/30 rounded-2xl p-8 shadow-2xl">
              {/* 关闭按钮 */}
              <button
                onClick={handleCloseModal}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/20 transition-colors"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>

              {/* 进度指示器 */}
              <div className="flex items-center justify-center mb-6">
                <div className="flex space-x-2">
                  {[1, 2, 3].map((step) => (
                    <div
                      key={step}
                      className={`w-3 h-3 rounded-full transition-all duration-300 ${
                        step <= currentStep
                          ? 'bg-gradient-to-r from-blue-500 to-purple-600 scale-110'
                          : 'bg-gray-300'
                      }`}
                    />
                  ))}
                </div>
              </div>

              {/* 问题内容 */}
              <div className="text-center mb-6">
                {currentStep === 1 && (
                  <div>
                    <h3 className="text-xl font-bold text-gray-800 mb-4">
                      请告诉我们您的年龄
                    </h3>
                    <p className="text-gray-600 mb-6">
                      这将帮助我们为您推荐合适难度的学习内容
                    </p>
                    <div className="space-y-3">
                      {['小学生 (6-12岁)', '初中生 (13-15岁)', '高中生 (16-18岁)', '大学生 (19-25岁)', '成年人 (25岁以上)'].map((age) => (
                        <button
                          key={age}
                          onClick={() => setUserAge(age)}
                          className={`option-button w-full p-3 rounded-xl border-2 transition-all text-left ${
                            userAge === age
                              ? 'border-blue-500 bg-blue-50/70 text-blue-700 transform scale-[1.02]'
                              : 'border-gray-200 hover:border-gray-300 hover:bg-white/60'
                          }`}
                        >
                          {age}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {currentStep === 2 && (
                  <div>
                    <h3 className="text-xl font-bold text-gray-800 mb-4">
                      您的学习目标是什么？
                    </h3>
                    <p className="text-gray-600 mb-6">
                      了解您的学习动机，为您制定更合适的学习计划
                    </p>
                    <div className="space-y-3">
                      {['系统学习 - 全面掌握知识体系', '满足好奇心 - 快速了解基础概念', '为了考试 - 重点突破考试要点'].map((goal) => (
                        <button
                          key={goal}
                          onClick={() => setLearningGoal(goal)}
                          className={`option-button w-full p-3 rounded-xl border-2 transition-all text-left ${
                            learningGoal === goal
                              ? 'border-blue-500 bg-blue-50/70 text-blue-700 transform scale-[1.02]'
                              : 'border-gray-200 hover:border-gray-300 hover:bg-white/60'
                          }`}
                        >
                          {goal}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {currentStep === 3 && (
                  <div>
                    <h3 className="text-xl font-bold text-gray-800 mb-4">
                      您希望花多长时间学习？
                    </h3>
                    <p className="text-gray-600 mb-6">
                      我们将根据您的时间安排制定学习计划
                    </p>
                    <div className="space-y-3">
                      {['一个小时的学习计划 - 快速入门', '几天的计划 - 深入理解', '几周的学习计划 - 全面掌握'].map((time) => (
                        <button
                          key={time}
                          onClick={() => setTimePreference(time)}
                          className={`option-button w-full p-3 rounded-xl border-2 transition-all text-left ${
                            timePreference === time
                              ? 'border-blue-500 bg-blue-50/70 text-blue-700 transform scale-[1.02]'
                              : 'border-gray-200 hover:border-gray-300 hover:bg-white/60'
                          }`}
                        >
                          {time}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 操作按钮 */}
              <div className="flex justify-between items-center">
                <Button
                  variant="outline"
                  onClick={currentStep === 1 ? handleCloseModal : () => setCurrentStep(currentStep - 1)}
                  className="bg-white/60 hover:bg-white/80 border-gray-200 backdrop-blur-sm"
                >
                  {currentStep === 1 ? '取消' : '上一步'}
                </Button>
                
                <Button
                  onClick={handleQuestionNext}
                  disabled={!isStepValid()}
                  className={`gradient-bg text-white shadow-lg transition-all duration-200 ${
                    isStepValid() ? 'hover:shadow-xl hover:scale-105' : 'opacity-50 cursor-not-allowed'
                  }`}
                >
                  {currentStep === 3 ? '开始生成课程' : '下一步'}
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Index;
