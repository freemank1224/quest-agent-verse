import React, { useState, useEffect } from 'react';
import { Progress } from '@/components/ui/progress';
import LoadingPlaceholder from '@/components/LoadingPlaceholder';
import { Button } from "@/components/ui/button";
import { useNavigate } from 'react-router-dom';
import { User } from '@supabase/supabase-js';
import { useChat } from '@/contexts/ChatContext';
import { getCourseOutline, checkCourseExists } from '@/services/api';
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ChevronDown, ChevronRight, Award, BookOpen, Target, CheckCircle, Clock, Users } from 'lucide-react';

// 布鲁姆分类层级的颜色映射
const BLOOM_COLORS = {
  remember: 'bg-red-100 text-red-700 border-red-200',
  understand: 'bg-orange-100 text-orange-700 border-orange-200',
  apply: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  analyze: 'bg-green-100 text-green-700 border-green-200',
  evaluate: 'bg-blue-100 text-blue-700 border-blue-200',
  create: 'bg-purple-100 text-purple-700 border-purple-200',
};

// 布鲁姆分类层级的中文映射
const BLOOM_LABELS = {
  remember: '记忆',
  understand: '理解',
  apply: '应用',
  analyze: '分析',
  evaluate: '评价',
  create: '创造',
};

interface CourseData {
  // 完整课程数据格式 (CoursePlanner 生成)
  course_title?: string;
  course_description?: string;
  background_analysis?: {
    target_age?: string;
    knowledge_level?: string;
    learning_context?: string;
  };
  bloom_taxonomy_objectives?: {
    [key: string]: string[];
  };
  curriculum_alignment?: {
    standards_used?: string;
    alignment_overview?: string;
  };
  // 简化课程数据格式 (缓存数据)
  title?: string;
  description?: string;
  topic?: string;
  saved_at?: string;
  chapters?: Array<{
    id: string;
    title: string;
    description?: string;
    estimated_duration?: string;
    bloom_focus?: string[];
    curriculum_alignment?: string;
    sections: Array<{
      id: string;
      title: string;
      content_type?: string;
    }>;
  }>;
}

interface EnhancedLearningProgressProps {
  userProgress: any;
  isLoadingProgress: boolean;
  user: User | null;
  initialPrompt?: string;
}

const EnhancedLearningProgress: React.FC<EnhancedLearningProgressProps> = ({ 
  userProgress, 
  isLoadingProgress,
  user,
  initialPrompt: propInitialPrompt
}) => {
  const navigate = useNavigate();
  const { messages, initialPrompt: contextInitialPrompt } = useChat();
  // 使用传入的 prop 或从 context 获取
  const initialPrompt = propInitialPrompt || contextInitialPrompt;
  const [courseData, setCourseData] = useState<CourseData | null>(null);
  const [isLoadingCourse, setIsLoadingCourse] = useState(true);
  const [currentSection, setCurrentSection] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<{[key: string]: boolean}>({
    course: true,
    progress: true,
    achievements: false,
    knowledge: false,
  });

  // 从聊天消息中提取知识点
  const extractKnowledgePoints = () => {
    const knowledgePoints: {[key: string]: string[]} = {
      remember: [],
      understand: [],
      apply: [],
      analyze: [],
      evaluate: [],
      create: [],
    };

    // 简单的关键词映射来模拟知识点提取
    const keywordMapping = {
      remember: ['概念', '定义', '术语', '记住', '回忆'],
      understand: ['理解', '解释', '说明', '描述', '阐述'],
      apply: ['应用', '使用', '实践', '操作', '演示'],
      analyze: ['分析', '比较', '对比', '分解', '探究'],
      evaluate: ['评价', '评估', '判断', '批评', '反思'],
      create: ['创造', '设计', '构建', '发明', '制作'],
    };

    messages.forEach(message => {
      if (message.sender === 'agent') {
        Object.entries(keywordMapping).forEach(([level, keywords]) => {
          keywords.forEach(keyword => {
            if (message.content.includes(keyword) && !knowledgePoints[level].includes(keyword)) {
              knowledgePoints[level].push(keyword);
            }
          });
        });
      }
    });

    return knowledgePoints;
  };

  // 计算学习进度
  const calculateProgress = () => {
    if (!courseData?.chapters || messages.length === 0) return 0;
    
    const totalSections = courseData.chapters.reduce((sum, chapter) => sum + chapter.sections.length, 0);
    const discussedTopics = Math.min(messages.filter(m => m.sender === 'user').length, totalSections);
    
    return Math.round((discussedTopics / totalSections) * 100);
  };

  // 获取成就状态
  const getAchievements = () => {
    const achievements = [];
    const messageCount = messages.length;
    const userMessages = messages.filter(m => m.sender === 'user').length;

    if (messageCount >= 5) {
      achievements.push({ id: 'starter', title: '开始学习', description: '发送了第一条消息', unlocked: true });
    }
    if (userMessages >= 10) {
      achievements.push({ id: 'engaged', title: '积极互动', description: '积极参与讨论', unlocked: true });
    }
    if (userMessages >= 20) {
      achievements.push({ id: 'explorer', title: '知识探索者', description: '深入探索学习内容', unlocked: true });
    }

    return achievements;
  };

  // 获取课程数据
  useEffect(() => {
    const fetchCourseData = async () => {
      if (!initialPrompt) {
        setIsLoadingCourse(false);
        return;
      }

      try {
        setIsLoadingCourse(true);
        
        // 首先检查是否已存在课程
        const existsResult = await checkCourseExists(initialPrompt);
        if (existsResult.exists && existsResult.course_data) {
          setCourseData(existsResult.course_data);
        } else {
          // 如果不存在，尝试获取课程大纲
          try {
            const outline = await getCourseOutline(initialPrompt);
            setCourseData(outline);
          } catch (error) {
            console.warn('Failed to get course outline:', error);
          }
        }
      } catch (error) {
        console.error('Error fetching course data:', error);
      } finally {
        setIsLoadingCourse(false);
      }
    };

    fetchCourseData();
  }, [initialPrompt]);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const progress = calculateProgress();
  const achievements = getAchievements();
  const knowledgePoints = extractKnowledgePoints();

  if (isLoadingProgress || isLoadingCourse) {
    return (
      <div className="space-y-6">
        <LoadingPlaceholder />
        <LoadingPlaceholder lines={5} />
        <LoadingPlaceholder lines={3} />
      </div>
    );
  }

  return (
    <div className="space-y-4 relative">
      {/* 固定的课程章节标题 - 毛玻璃效果，最高 Z-index */}
      {courseData?.chapters && courseData.chapters.length > 0 && (
        <div className="sticky top-0 z-50 backdrop-blur-md bg-white/90 border-b border-gray-200/60 px-3 py-2 -mx-3 mb-4 shadow-sm">
          <h3 className="text-sm font-medium text-gray-900 flex items-center space-x-2">
            <BookOpen className="w-4 h-4 text-blue-600" />
            <span>课程章节</span>
            <Badge variant="outline" className="text-xs ml-auto">
              {courseData.chapters.length}章
            </Badge>
          </h3>
        </div>
      )}

      {/* 课程信息概览 */}
      <Card>
        <CardHeader 
          className="pb-3 cursor-pointer"
          onClick={() => toggleSection('course')}
        >
          <CardTitle className="flex items-center justify-between text-sm font-medium">
            <div className="flex items-center space-x-2">
              <BookOpen className="w-4 h-4" />
              <span>课程概览</span>
            </div>
            {expandedSections.course ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </CardTitle>
        </CardHeader>
        {expandedSections.course && (
          <CardContent className="pt-0">
            {courseData ? (
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-sm text-gray-900">
                    {courseData.course_title || courseData.title || initialPrompt}
                  </h4>
                  {(courseData.course_description || courseData.description) && (
                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                      {courseData.course_description || courseData.description}
                    </p>
                  )}
                </div>
                
                {courseData.background_analysis && (
                  <div className="flex flex-wrap gap-1">
                    {courseData.background_analysis.target_age && (
                      <Badge variant="secondary" className="text-xs">
                        <Users className="w-3 h-3 mr-1" />
                        {courseData.background_analysis.target_age}
                      </Badge>
                    )}
                    {courseData.background_analysis.knowledge_level && (
                      <Badge variant="secondary" className="text-xs">
                        📚 {courseData.background_analysis.knowledge_level}
                      </Badge>
                    )}
                  </div>
                )}

                {courseData.curriculum_alignment && (
                  <div className="text-xs">
                    <div className="flex items-center space-x-1">
                      <CheckCircle className="w-3 h-3 text-green-600" />
                      <span className="text-green-700 font-medium">课标对齐</span>
                    </div>
                    <p className="text-gray-600 mt-1">
                      {courseData.curriculum_alignment.standards_used || '标准课程体系'}
                    </p>
                  </div>
                )}

                {/* 显示完整课程章节信息 */}
                {courseData.chapters && courseData.chapters.length > 0 && (
                  <div className="mt-4 space-y-3">
                    <Separator />
                    <h5 className="text-xs font-medium text-gray-700">完整课程章节</h5>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {courseData.chapters.map((chapter, chapterIndex) => (
                        <div key={chapter.id} className="space-y-1">
                          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span className="text-xs font-medium text-gray-800">
                              第{chapterIndex + 1}章: {chapter.title}
                            </span>
                            {chapter.description && (
                              <Badge variant="outline" className="text-xs">
                                {chapter.sections?.length || 0}节
                              </Badge>
                            )}
                          </div>
                          {chapter.description && (
                            <p className="text-xs text-gray-600 ml-2 mb-1">
                              {chapter.description}
                            </p>
                          )}
                          {chapter.sections && (
                            <div className="ml-4 space-y-1">
                              {chapter.sections.map((section, sectionIndex) => (                              <div 
                                key={section.id} 
                                className={`text-xs p-1.5 rounded transition-colors cursor-pointer relative z-10 ${
                                  currentSection === section.id 
                                    ? 'bg-purple-100 text-purple-800 border border-purple-200 shadow-sm' 
                                    : 'text-gray-600 hover:bg-gray-100'
                                }`}
                                onClick={() => setCurrentSection(section.id)}
                              >
                                {chapterIndex + 1}.{sectionIndex + 1} {section.title}
                              </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-xs text-gray-500">
                <div className="flex items-center space-x-2">
                  <Target className="w-4 h-4" />
                  <span>当前学习主题: {initialPrompt}</span>
                </div>
                <p className="mt-1">正在分析课程内容...</p>
              </div>
            )}
          </CardContent>
        )}
      </Card>

      {/* 学习进度 */}
      <Card>
        <CardHeader 
          className="pb-3 cursor-pointer"
          onClick={() => toggleSection('progress')}
        >
          <CardTitle className="flex items-center justify-between text-sm font-medium">
            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4" />
              <span>学习进度</span>
            </div>
            {expandedSections.progress ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </CardTitle>
        </CardHeader>
        {expandedSections.progress && (
          <CardContent className="pt-0">
            <div className="space-y-3">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs text-gray-600">完成度</span>
                  <span className="text-xs font-medium">{progress}%</span>
                </div>
                <Progress value={progress} className="h-2" />
              </div>
              
              {courseData?.chapters && (
                <div className="space-y-2">
                  <h5 className="text-xs font-medium text-gray-700">近期章节</h5>
                  {courseData.chapters.slice(0, 3).map((chapter, chapterIndex) => (
                    <div key={chapter.id} className="text-xs">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600 truncate">
                          第{chapterIndex + 1}章: {chapter.title}
                        </span>
                        <div className="flex items-center space-x-1">
                          {chapter.estimated_duration && (
                            <Badge variant="outline" className="text-xs px-1 py-0">
                              <Clock className="w-2 h-2 mr-1" />
                              {chapter.estimated_duration}
                            </Badge>
                          )}
                        </div>
                      </div>
                      {chapter.sections && (
                        <div className="ml-2 mt-1 space-y-1">
                          {chapter.sections.slice(0, 2).map((section, sectionIndex) => (
                            <div key={section.id} className="text-xs text-gray-500">
                              {chapterIndex + 1}.{sectionIndex + 1} {section.title}
                            </div>
                          ))}
                          {chapter.sections.length > 2 && (
                            <div className="text-xs text-gray-400">
                              +{chapter.sections.length - 2} 更多小节
                            </div>
                          )}
                        </div>
                      )}
                      {chapter.bloom_focus && chapter.bloom_focus.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {chapter.bloom_focus.slice(0, 2).map((focus) => (
                            <Badge 
                              key={focus}
                              className={`text-xs px-1 py-0 ${BLOOM_COLORS[focus as keyof typeof BLOOM_COLORS] || 'bg-gray-100 text-gray-700'}`}
                            >
                              {BLOOM_LABELS[focus as keyof typeof BLOOM_LABELS] || focus}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                  {courseData.chapters.length > 3 && (
                    <p className="text-xs text-gray-500">还有 {courseData.chapters.length - 3} 个章节...</p>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        )}
      </Card>

      {/* 成就系统 */}
      <Card>
        <CardHeader 
          className="pb-3 cursor-pointer"
          onClick={() => toggleSection('achievements')}
        >
          <CardTitle className="flex items-center justify-between text-sm font-medium">
            <div className="flex items-center space-x-2">
              <Award className="w-4 h-4" />
              <span>学习成就</span>
              <Badge variant="secondary" className="text-xs">
                {achievements.length}
              </Badge>
            </div>
            {expandedSections.achievements ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </CardTitle>
        </CardHeader>
        {expandedSections.achievements && (
          <CardContent className="pt-0">
            <div className="space-y-2">
              {achievements.length > 0 ? (
                achievements.map((achievement) => (
                  <div key={achievement.id} className="flex items-start space-x-2 p-2 rounded-lg bg-green-50 border border-green-200">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-green-800">{achievement.title}</p>
                      <p className="text-xs text-green-600">{achievement.description}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-gray-500 text-center py-2">
                  <Award className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                  <p>继续学习解锁成就</p>
                </div>
              )}
            </div>
          </CardContent>
        )}
      </Card>

      {/* 知识点分析 */}
      <Card>
        <CardHeader 
          className="pb-3 cursor-pointer"
          onClick={() => toggleSection('knowledge')}
        >
          <CardTitle className="flex items-center justify-between text-sm font-medium">
            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4" />
              <span>知识点分析</span>
            </div>
            {expandedSections.knowledge ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </CardTitle>
        </CardHeader>
        {expandedSections.knowledge && (
          <CardContent className="pt-0">
            <div className="space-y-3">
              <p className="text-xs text-gray-600">基于布鲁姆分类法的认知层级</p>
              
              {Object.entries(knowledgePoints).map(([level, points]) => (
                <div key={level} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className={`text-xs px-2 py-1 rounded border ${BLOOM_COLORS[level as keyof typeof BLOOM_COLORS]}`}>
                      {BLOOM_LABELS[level as keyof typeof BLOOM_LABELS]}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      {points.length}
                    </Badge>
                  </div>
                  {points.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {points.slice(0, 3).map((point, index) => (
                        <Badge key={index} variant="outline" className="text-xs px-1 py-0">
                          {point}
                        </Badge>
                      ))}
                      {points.length > 3 && (
                        <span className="text-xs text-gray-500">+{points.length - 3}</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        )}
      </Card>

      {/* 课程大纲布鲁姆目标 */}
      {courseData?.bloom_taxonomy_objectives && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center space-x-2">
              <Target className="w-4 h-4" />
              <span>课程学习目标</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-2">
              {Object.entries(courseData.bloom_taxonomy_objectives).map(([level, objectives]) => (
                objectives && objectives.length > 0 && (
                  <div key={level} className="space-y-1">
                    <Badge className={`text-xs ${BLOOM_COLORS[level as keyof typeof BLOOM_COLORS]}`}>
                      {BLOOM_LABELS[level as keyof typeof BLOOM_LABELS]}
                    </Badge>
                    <ul className="text-xs text-gray-600 ml-2 space-y-1">
                      {objectives.slice(0, 2).map((objective, index) => (
                        <li key={index} className="flex items-start space-x-1">
                          <span className="text-gray-400 mt-1">•</span>
                          <span className="line-clamp-2">{objective}</span>
                        </li>
                      ))}
                      {objectives.length > 2 && (
                        <li className="text-gray-400 text-xs">+{objectives.length - 2} 更多</li>
                      )}
                    </ul>
                  </div>
                )
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 用户登录提示 */}
      {!user && (
        <Card>
          <CardContent className="pt-4">
            <div className="text-center space-y-2">
              <Users className="w-8 h-8 mx-auto text-gray-400" />
              <h4 className="text-sm font-medium text-gray-900">保存学习进度</h4>
              <p className="text-xs text-gray-600">
                登录以保存您的学习进度和成就
              </p>
              <Button 
                onClick={() => navigate('/auth')} 
                size="sm" 
                className="w-full"
              >
                登录 / 注册
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default EnhancedLearningProgress;
