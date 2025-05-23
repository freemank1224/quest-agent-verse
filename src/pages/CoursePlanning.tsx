import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import Navbar from '@/components/Navbar';
import MarkdownRenderer from '@/components/MarkdownRenderer';
import LoadingPlaceholder from '@/components/LoadingPlaceholder';
import { useChat } from '@/contexts/ChatContext';
import { getCourseOutline, getCourseContent, checkCourseExists } from '@/services/api';
import { toast } from '@/components/ui/sonner';
import { Separator } from '@/components/ui/separator';

interface Section {
  id: string;
  title: string;
}

interface Chapter {
  id: string;
  title: string;
  sections: Section[];
}

interface CourseOutline {
  title: string;
  chapters: Chapter[];
}

interface CourseContent {
  title: string;
  mainContent: string;
  keyPoints: string[];
  images: { url: string; caption: string }[];
  curriculumAlignment: string[];
}

const CoursePlanning = () => {
  const navigate = useNavigate();
  const { initialPrompt } = useChat();
  const [outline, setOutline] = useState<CourseOutline | null>(null);
  const [content, setContent] = useState<CourseContent | null>(null);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [isLoadingOutline, setIsLoadingOutline] = useState(true);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [courseSource, setCourseSource] = useState<string>(''); // 'cache', 'api', 'localStorage'

  // 生成课程缓存key
  const getCourseStorageKey = (topic: string) => `course_outline_${topic.replace(/\s+/g, '_')}`;
  const getSectionStorageKey = (topic: string, sectionId: string) => 
    `course_section_${topic.replace(/\s+/g, '_')}_${sectionId}`;

  // 保存课程到localStorage
  const saveCourseToStorage = (topic: string, courseData: CourseOutline) => {
    try {
      const storageKey = getCourseStorageKey(topic);
      const dataToStore = {
        ...courseData,
        cachedAt: new Date().toISOString(),
        topic: topic
      };
      localStorage.setItem(storageKey, JSON.stringify(dataToStore));
      console.log('Course saved to localStorage:', storageKey);
    } catch (error) {
      console.error('Error saving course to localStorage:', error);
    }
  };

  // 从localStorage加载课程
  const loadCourseFromStorage = (topic: string): CourseOutline | null => {
    try {
      const storageKey = getCourseStorageKey(topic);
      const storedData = localStorage.getItem(storageKey);
      if (storedData) {
        const parsedData = JSON.parse(storedData);
        console.log('Course loaded from localStorage:', storageKey);
        return parsedData;
      }
    } catch (error) {
      console.error('Error loading course from localStorage:', error);
    }
    return null;
  };

  // 保存章节内容到localStorage
  const saveSectionToStorage = (topic: string, sectionId: string, sectionData: CourseContent) => {
    try {
      const storageKey = getSectionStorageKey(topic, sectionId);
      const dataToStore = {
        ...sectionData,
        cachedAt: new Date().toISOString(),
        topic: topic,
        sectionId: sectionId
      };
      localStorage.setItem(storageKey, JSON.stringify(dataToStore));
      console.log('Section saved to localStorage:', storageKey);
    } catch (error) {
      console.error('Error saving section to localStorage:', error);
    }
  };

  // 从localStorage加载章节内容
  const loadSectionFromStorage = (topic: string, sectionId: string): CourseContent | null => {
    try {
      const storageKey = getSectionStorageKey(topic, sectionId);
      const storedData = localStorage.getItem(storageKey);
      if (storedData) {
        const parsedData = JSON.parse(storedData);
        console.log('Section loaded from localStorage:', storageKey);
        return parsedData;
      }
    } catch (error) {
      console.error('Error loading section from localStorage:', error);
    }
    return null;
  };

  useEffect(() => {
    const fetchCourseOutline = async () => {
      if (!initialPrompt) {
        // If there's no initial prompt, navigate back to the landing page
        toast.error('请先输入您想学习的内容');
        navigate('/');
        return;
      }

      try {
        setIsLoadingOutline(true);
        console.log('Fetching course outline for:', initialPrompt);
        
        // 1. 首先检查localStorage缓存
        const cachedOutline = loadCourseFromStorage(initialPrompt);
        if (cachedOutline) {
          console.log('Using cached course outline from localStorage');
          setOutline(cachedOutline);
          setCourseSource('localStorage');
          
          // Select the first section by default
          if (cachedOutline.chapters.length > 0 && cachedOutline.chapters[0].sections.length > 0) {
            setSelectedSection(cachedOutline.chapters[0].sections[0].id);
          }
          setIsLoadingOutline(false);
          return;
        }

        // 2. 检查后端是否已有课程
        const existsResult = await checkCourseExists(initialPrompt);
        if (existsResult.exists) {
          console.log(`Course found in ${existsResult.source}, using existing course`);
          const courseData = existsResult.course_data;
          
          // 验证和清理数据
          const validatedData = {
            title: courseData?.title || `${initialPrompt} 课程大纲`,
            chapters: Array.isArray(courseData?.chapters) ? courseData.chapters : []
          };
          
          // 确保每个章节都有必要的属性
          validatedData.chapters = validatedData.chapters.map((chapter, index) => ({
            id: chapter?.id || `chapter-${index + 1}`,
            title: chapter?.title || `第${index + 1}章`,
            description: chapter?.description || '',
            sections: Array.isArray(chapter?.sections) ? chapter.sections.map((section, sectionIndex) => ({
              id: section?.id || `${chapter?.id || (index + 1)}.${sectionIndex + 1}`,
              title: section?.title || `第${sectionIndex + 1}节`
            })) : [
              {
                id: `${chapter?.id || (index + 1)}.1`,
                title: `${chapter?.title || `第${index + 1}章`} - 详细内容`
              }
            ]
          }));

          setOutline(validatedData);
          setCourseSource(existsResult.source);
          
          // 保存到localStorage
          saveCourseToStorage(initialPrompt, validatedData);
          
          // Select the first section by default
          if (validatedData.chapters.length > 0 && validatedData.chapters[0].sections.length > 0) {
            setSelectedSection(validatedData.chapters[0].sections[0].id);
          }
          setIsLoadingOutline(false);
          return;
        }

        // 3. 如果都没有，生成新的课程内容
        console.log('No existing course found, generating new course');
        toast.info('正在为您生成全新的课程大纲...');
        
        const data = await getCourseOutline(
          initialPrompt,
          '深入理解主题内容',  // 默认学习目标
          '4-6小时',          // 默认学习时长
          '初学者'            // 默认背景知识水平
        );
        
        console.log('Raw API response:', data);
        
        // 验证和清理数据
        const validatedData = {
          title: data?.title || `${initialPrompt} 课程大纲`,
          chapters: Array.isArray(data?.chapters) ? data.chapters : []
        };
        
        // 确保每个章节都有必要的属性
        validatedData.chapters = validatedData.chapters.map((chapter, index) => ({
          id: chapter?.id || `chapter-${index + 1}`,
          title: chapter?.title || `第${index + 1}章`,
          description: chapter?.description || '',
          sections: Array.isArray(chapter?.sections) ? chapter.sections.map((section, sectionIndex) => ({
            id: section?.id || `${chapter?.id || (index + 1)}.${sectionIndex + 1}`,
            title: section?.title || `第${sectionIndex + 1}节`
          })) : [
            {
              id: `${chapter?.id || (index + 1)}.1`,
              title: `${chapter?.title || `第${index + 1}章`} - 详细内容`
            }
          ]
        }));
        
        console.log('Validated data:', validatedData);
        setOutline(validatedData);
        setCourseSource('api');
        
        // 保存到localStorage
        saveCourseToStorage(initialPrompt, validatedData);
        
        // Select the first section by default
        if (validatedData.chapters.length > 0 && validatedData.chapters[0].sections.length > 0) {
          setSelectedSection(validatedData.chapters[0].sections[0].id);
        }
        
        toast.success('课程大纲生成完成！');
      } catch (error) {
        console.error('Error fetching course outline:', error);
        toast.error('获取课程大纲失败，请重试');
        
        // 设置一个默认的课程大纲以防止页面崩溃
        const fallbackOutline = {
          title: `${initialPrompt} 课程大纲`,
          chapters: [
            {
              id: "1",
              title: "第一章：基础介绍",
              description: `介绍${initialPrompt}的基本概念`,
              sections: [
                { id: "1.1", title: "概念介绍" },
                { id: "1.2", title: "基础知识" }
              ]
            },
            {
              id: "2",
              title: "第二章：深入学习", 
              description: `深入学习${initialPrompt}的核心内容`,
              sections: [
                { id: "2.1", title: "核心原理" },
                { id: "2.2", title: "实际应用" }
              ]
            }
          ]
        };
        setOutline(fallbackOutline);
        setSelectedSection("1.1");
        setCourseSource('fallback');
      } finally {
        setIsLoadingOutline(false);
      }
    };

    fetchCourseOutline();
  }, [initialPrompt, navigate]);

  useEffect(() => {
    const fetchSectionContent = async () => {
      if (!selectedSection || !initialPrompt) return;

      try {
        setIsLoadingContent(true);
        
        // 1. 首先检查localStorage缓存
        const cachedContent = loadSectionFromStorage(initialPrompt, selectedSection);
        if (cachedContent) {
          console.log('Using cached section content from localStorage');
          setContent(cachedContent);
          setIsLoadingContent(false);
          return;
        }

        // 2. 如果没有缓存，从API获取
        console.log('Fetching section content from API');
        const data = await getCourseContent(selectedSection, initialPrompt);
        setContent(data);
        
        // 保存到localStorage
        saveSectionToStorage(initialPrompt, selectedSection, data);
        
      } catch (error) {
        console.error('Error fetching section content:', error);
        toast.error('获取章节内容失败，请重试');
      } finally {
        setIsLoadingContent(false);
      }
    };

    fetchSectionContent();
  }, [selectedSection, initialPrompt]);

  const handleStartLearning = () => {
    navigate('/interactive-learning');
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      
      <main className="flex-grow flex flex-col md:flex-row">
        {/* Left sidebar - Course outline */}
        <div className="w-full md:w-1/4 bg-white shadow-sm p-4 md:p-6 overflow-y-auto max-h-[calc(100vh-4rem)]">
          <h2 className="text-xl font-bold mb-4 font-display">课程大纲</h2>
          
          {/* 显示内容来源 */}
          {courseSource && (
            <div className="mb-4 text-xs text-gray-500">
              {courseSource === 'localStorage' && '📱 从本地缓存加载'}
              {courseSource === 'memory' && '🧠 从记忆库加载'}
              {courseSource === 'file' && '📄 从文件加载'}
              {courseSource === 'api' && '🆕 新生成的内容'}
              {courseSource === 'fallback' && '⚠️ 默认内容'}
            </div>
          )}
          
          {isLoadingOutline ? (
            <LoadingPlaceholder lines={10} />
          ) : outline ? (
            <div>
              <h3 className="text-lg font-semibold mb-2">{outline.title}</h3>
              <div className="space-y-4 mt-4">
                {outline.chapters && outline.chapters.length > 0 ? (
                  outline.chapters.map((chapter) => (
                    <div key={chapter.id} className="space-y-2">
                      <h4 className="font-medium text-gray-900">{chapter.title}</h4>
                      <ul className="ml-4 space-y-1">
                        {chapter.sections && chapter.sections.length > 0 ? (
                          chapter.sections.map((section) => (
                            <li key={section.id}>
                              <button
                                onClick={() => setSelectedSection(section.id)}
                                className={`text-left w-full p-1.5 text-sm rounded hover:bg-gray-100 ${
                                  selectedSection === section.id
                                    ? 'bg-primary/10 text-primary font-medium'
                                    : 'text-gray-700'
                                }`}
                              >
                                {section.title}
                              </button>
                            </li>
                          ))
                        ) : (
                          <li className="text-sm text-gray-500 ml-4">暂无章节内容</li>
                        )}
                      </ul>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500">暂无课程章节</p>
                )}
              </div>
              <div className="mt-8">
                <Button onClick={handleStartLearning} className="w-full">
                  开始学习
                </Button>
              </div>
            </div>
          ) : (
            <p>没有可用的课程大纲</p>
          )}
        </div>
        
        {/* Right area - Content */}
        <div className="flex-grow p-4 md:p-8 overflow-y-auto max-h-[calc(100vh-4rem)]">
          {isLoadingContent ? (
            <div className="space-y-8">
              <LoadingPlaceholder type="image" />
              <LoadingPlaceholder lines={8} />
              <LoadingPlaceholder lines={3} />
            </div>
          ) : content ? (
            <div className="max-w-3xl mx-auto">
              <h2 className="text-2xl font-bold mb-6 font-display">{content.title}</h2>
              
              {/* Images section */}
              {content.images && content.images.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-lg font-semibold mb-4">图片资源</h3>
                  <div className="grid grid-cols-1 gap-4">
                    {content.images.map((image, index) => (
                      <figure key={index} className="rounded-lg overflow-hidden shadow-md">
                        <img 
                          src={image.url} 
                          alt={image.caption} 
                          className="w-full h-auto object-cover"
                        />
                        <figcaption className="p-2 text-sm text-gray-600 bg-gray-50">
                          {image.caption}
                        </figcaption>
                      </figure>
                    ))}
                  </div>
                </div>
              )}
              
              <Separator className="my-6" />
              
              {/* Main content */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold mb-4">主要内容</h3>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <MarkdownRenderer content={content.mainContent} />
                </div>
              </div>
              
              <Separator className="my-6" />
              
              {/* Key points */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold mb-4">核心知识点</h3>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <ul className="list-disc list-inside space-y-2">
                    {content.keyPoints.map((point, index) => (
                      <li key={index} className="text-gray-800">{point}</li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <Separator className="my-6" />
              
              {/* Curriculum alignment */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold mb-4">课标对齐</h3>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <ul className="list-disc list-inside space-y-2">
                    {content.curriculumAlignment.map((alignment, index) => (
                      <li key={index} className="text-gray-800">{alignment}</li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <div className="mt-8 flex justify-center">
                <Button onClick={handleStartLearning} size="lg">
                  开始互动学习
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full">
              <p className="text-gray-500">请选择一个章节以查看内容</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default CoursePlanning;
