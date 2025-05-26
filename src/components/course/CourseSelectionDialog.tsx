import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { toast } from "@/components/ui/sonner";
import { getCourseList } from '@/services/api';
import LoadingPlaceholder from '@/components/LoadingPlaceholder';
import { BookOpen, Clock, Users, Search, Plus, CheckCircle2, AlertCircle } from 'lucide-react';

interface Course {
  filename: string;
  topic: string;
  title: string;
  saved_at: string;
  chapters_count: number;
  course_data?: any;
  completeness?: {
    total_sections: number;
    cached_sections: number;
    complete_outline: boolean;
    status: 'complete' | 'incomplete_content' | 'incomplete_outline' | 'empty';
  };
}

interface CourseSelectionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  topic: string;
  backgroundInfo?: string;
  onSelectExisting: (course: Course) => void;
  onCreateNew: () => void;
}

const CourseSelectionDialog: React.FC<CourseSelectionDialogProps> = ({
  isOpen,
  onClose,
  topic,
  backgroundInfo,
  onSelectExisting,
  onCreateNew
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [courses, setCourses] = useState<Course[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);

  // 搜索并加载课程
  useEffect(() => {
    if (isOpen) {
      fetchCourses();
      // 自动搜索相关课程
      setSearchTerm(topic);
    }
  }, [isOpen, topic]);

  // 过滤课程
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredCourses(courses);
    } else {
      const filtered = courses.filter(course =>
        course.topic.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredCourses(filtered);
    }
  }, [searchTerm, courses]);

  const fetchCourses = async () => {
    try {
      setIsLoading(true);
      const response = await getCourseList();
      const coursesWithCompleteness = response.courses.map((course: Course) => ({
        ...course,
        completeness: analyzeCourseCompleteness(course)
      }));
      setCourses(coursesWithCompleteness);
    } catch (error) {
      console.error('Error fetching courses:', error);
      toast.error('获取课程列表失败');
    } finally {
      setIsLoading(false);
    }
  };

  // 分析课程完整性
  const analyzeCourseCompleteness = (course: Course): Course['completeness'] => {
    // 这里模拟课程完整性分析，实际应该从 course_data 中分析
    const totalSections = Math.max(course.chapters_count * 2, 1); // 估算章节数
    const cachedSections = Math.floor(Math.random() * totalSections); // 模拟缓存章节数
    
    let status: 'complete' | 'incomplete_content' | 'incomplete_outline' | 'empty';
    const completeOutline = course.chapters_count > 0;
    
    if (!completeOutline) {
      status = 'incomplete_outline';
    } else if (cachedSections === totalSections) {
      status = 'complete';
    } else if (cachedSections > 0) {
      status = 'incomplete_content';
    } else {
      status = 'empty';
    }

    return {
      total_sections: totalSections,
      cached_sections: cachedSections,
      complete_outline: completeOutline,
      status
    };
  };

  const getStatusInfo = (completeness?: Course['completeness']) => {
    if (!completeness) return { color: 'gray', text: '未知状态', icon: AlertCircle };

    switch (completeness.status) {
      case 'complete':
        return { 
          color: 'green', 
          text: '完整课程', 
          icon: CheckCircle2,
          description: '所有内容已生成，可直接学习'
        };
      case 'incomplete_content':
        return { 
          color: 'yellow', 
          text: '部分内容', 
          icon: AlertCircle,
          description: '大纲完整，需补充缺失章节内容'
        };
      case 'incomplete_outline':
        return { 
          color: 'orange', 
          text: '大纲不完整', 
          icon: AlertCircle,
          description: '课程大纲需要重新生成'
        };
      case 'empty':
        return { 
          color: 'red', 
          text: '空课程', 
          icon: AlertCircle,
          description: '仅有基本信息，需要生成全部内容'
        };
      default:
        return { color: 'gray', text: '未知', icon: AlertCircle };
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '未知时间';
    try {
      return new Date(dateString).toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '未知时间';
    }
  };

  const handleSelectCourse = (course: Course) => {
    setSelectedCourse(course);
  };

  const handleConfirmSelection = () => {
    if (selectedCourse) {
      onSelectExisting(selectedCourse);
      onClose();
    }
  };

  const handleCreateNew = () => {
    onCreateNew();
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold flex items-center space-x-2">
            <BookOpen className="w-6 h-6 text-blue-600" />
            <span>选择学习课程</span>
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 flex flex-col space-y-4 overflow-hidden">
          {/* 学习主题和背景信息 */}
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h3 className="font-medium text-blue-900 mb-2">当前学习主题</h3>
            <p className="text-blue-800 font-medium">{topic}</p>
            {backgroundInfo && (
              <p className="text-blue-700 text-sm mt-1">{backgroundInfo}</p>
            )}
          </div>

          {/* 搜索栏 */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              placeholder="搜索相关课程..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* 操作按钮 */}
          <div className="flex space-x-3">
            <Button
              onClick={handleCreateNew}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              创建新课程
            </Button>
            {selectedCourse && (
              <Button
                onClick={handleConfirmSelection}
                variant="outline"
                className="flex-1"
              >
                <CheckCircle2 className="w-4 h-4 mr-2" />
                使用选中课程
              </Button>
            )}
          </div>

          <Separator />

          {/* 课程列表 */}
          <div className="flex-1 overflow-y-auto space-y-3">
            {isLoading ? (
              <div className="space-y-3">
                <LoadingPlaceholder lines={3} />
                <LoadingPlaceholder lines={3} />
                <LoadingPlaceholder lines={3} />
              </div>
            ) : filteredCourses.length === 0 ? (
              <div className="text-center py-8">
                <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">
                  {courses.length === 0 ? '暂无已保存的课程' : '未找到匹配的课程'}
                </p>
                <p className="text-gray-400 text-sm mt-1">
                  {courses.length === 0 ? '创建您的第一个课程开始学习' : '尝试调整搜索条件'}
                </p>
              </div>
            ) : (
              filteredCourses.map((course) => {
                const statusInfo = getStatusInfo(course.completeness);
                const StatusIcon = statusInfo.icon;
                const isSelected = selectedCourse?.filename === course.filename;

                return (
                  <Card
                    key={course.filename}
                    className={`cursor-pointer transition-all duration-200 ${
                      isSelected
                        ? 'ring-2 ring-blue-500 border-blue-500 bg-blue-50'
                        : 'hover:shadow-md border-gray-200'
                    }`}
                    onClick={() => handleSelectCourse(course)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg font-medium text-gray-900 mb-1">
                            {course.title}
                          </CardTitle>
                          <p className="text-sm text-gray-600">{course.topic}</p>
                        </div>
                        <div className="flex flex-col items-end space-y-2">
                          <Badge
                            variant="outline"
                            className={`text-xs ${
                              statusInfo.color === 'green' ? 'border-green-500 text-green-700 bg-green-50' :
                              statusInfo.color === 'yellow' ? 'border-yellow-500 text-yellow-700 bg-yellow-50' :
                              statusInfo.color === 'orange' ? 'border-orange-500 text-orange-700 bg-orange-50' :
                              statusInfo.color === 'red' ? 'border-red-500 text-red-700 bg-red-50' :
                              'border-gray-500 text-gray-700 bg-gray-50'
                            }`}
                          >
                            <StatusIcon className="w-3 h-3 mr-1" />
                            {statusInfo.text}
                          </Badge>
                          {isSelected && (
                            <Badge className="bg-blue-600 text-white text-xs">
                              已选择
                            </Badge>
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="space-y-3">
                        {/* 状态描述 */}
                        <p className="text-xs text-gray-600">
                          {statusInfo.description}
                        </p>

                        {/* 课程统计 */}
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <div className="flex items-center space-x-4">
                            <span className="flex items-center space-x-1">
                              <BookOpen className="w-3 h-3" />
                              <span>{course.chapters_count} 章</span>
                            </span>
                            {course.completeness && (
                              <span className="flex items-center space-x-1">
                                <CheckCircle2 className="w-3 h-3" />
                                <span>
                                  {course.completeness.cached_sections}/{course.completeness.total_sections} 节
                                </span>
                              </span>
                            )}
                          </div>
                          <div className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>{formatDate(course.saved_at)}</span>
                          </div>
                        </div>

                        {/* 进度条 */}
                        {course.completeness && course.completeness.total_sections > 0 && (
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all duration-300 ${
                                statusInfo.color === 'green' ? 'bg-green-500' :
                                statusInfo.color === 'yellow' ? 'bg-yellow-500' :
                                statusInfo.color === 'orange' ? 'bg-orange-500' :
                                'bg-red-500'
                              }`}
                              style={{
                                width: `${(course.completeness.cached_sections / course.completeness.total_sections) * 100}%`
                              }}
                            />
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CourseSelectionDialog;
