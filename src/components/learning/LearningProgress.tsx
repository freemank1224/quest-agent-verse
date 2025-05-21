
import React from 'react';
import { Progress } from '@/components/ui/progress';
import LoadingPlaceholder from '@/components/LoadingPlaceholder';
import { Button } from "@/components/ui/button";
import { useNavigate } from 'react-router-dom';
import { User } from '@supabase/supabase-js';

interface LearningProgressProps {
  userProgress: any;
  isLoadingProgress: boolean;
  user: User | null;
}

const LearningProgress: React.FC<LearningProgressProps> = ({ 
  userProgress, 
  isLoadingProgress,
  user 
}) => {
  const navigate = useNavigate();
  
  if (isLoadingProgress) {
    return (
      <div className="space-y-6">
        <LoadingPlaceholder />
        <LoadingPlaceholder lines={5} />
      </div>
    );
  }

  if (!userProgress) {
    return <p className="text-gray-500">无法加载学习资源</p>;
  }

  return (
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
  );
};

export default LearningProgress;
