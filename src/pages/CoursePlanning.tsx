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
  content_type?: string;
  activity_suggestion?: string;
}

interface BloomTaxonomyObjectives {
  remember: string[];
  understand: string[];
  apply: string[];
  analyze: string[];
  evaluate: string[];
  create: string[];
}

interface TeachingResources {
  interactive_activities: string[];
  media_types: string[];
  assessment_methods: string[];
}

interface ContentDesignGuidance {
  content_structure: string;
  difficulty_level: string;
  examples_needed: string;
  practice_activities: string;
}

interface BackgroundAnalysis {
  target_age: string;
  knowledge_level: string;
  learning_context: string;
}

interface CurriculumAlignment {
  standards_used: string;
  alignment_overview: string;
}

interface Chapter {
  id: string;
  title: string;
  description?: string;
  estimated_duration?: string;
  bloom_focus?: string[];
  learning_objectives?: string[];
  key_concepts?: string[];
  teaching_resources?: TeachingResources;
  content_design_guidance?: ContentDesignGuidance;
  curriculum_alignment?: string;
  sections: Section[];
}

interface CourseOutline {
  course_title?: string;
  course_description?: string;
  background_analysis?: BackgroundAnalysis;
  bloom_taxonomy_objectives?: BloomTaxonomyObjectives;
  curriculum_alignment?: CurriculumAlignment;
  chapters: Chapter[];
  // Legacy support for existing API responses
  title?: string;
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
  const { initialPrompt, setHasCourseGenerated } = useChat();
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
        console.log('Raw cached data structure:', {
          hasSections: Array.isArray(parsedData.sections),
          hasChapters: Array.isArray(parsedData.chapters),
          sectionsCount: parsedData.sections?.length || 0,
          chaptersCount: parsedData.chapters?.length || 0
        });
        
        // 处理数据结构转换：如果是旧的sections格式，转换为chapters格式
        let chaptersData = [];
        if (Array.isArray(parsedData.sections)) {
          console.log('Converting cached sections to chapters format');
          chaptersData = parsedData.sections.map((section, index) => ({
            id: section?.id || `chapter-${index + 1}`,
            title: section?.title || `第${index + 1}章`,
            description: section?.description || '',
            estimated_duration: section?.estimated_duration,
            bloom_focus: section?.bloom_focus,
            learning_objectives: section?.learning_objectives,
            key_concepts: section?.key_points || section?.key_concepts,
            teaching_resources: section?.teaching_resources,
            content_design_guidance: section?.content_design_guidance,
            curriculum_alignment: section?.curriculum_alignment,
            sections: Array.isArray(section?.subsections) ? section.subsections.map((subsection, subIndex) => ({
              id: subsection?.id || `${section?.id || (index + 1)}.${subIndex + 1}`,
              title: subsection?.title || `第${subIndex + 1}节`,
              content_type: subsection?.content_type,
              activity_suggestion: subsection?.activity_suggestion
            })) : [
              {
                id: `${section?.id || (index + 1)}.1`,
                title: `${section?.title || `第${index + 1}章`} - 详细内容`
              }
            ]
          }));
        } else if (Array.isArray(parsedData.chapters)) {
          console.log('Using existing cached chapters format');
          chaptersData = parsedData.chapters;
        } else {
          console.warn('No valid data structure found in cached data');
          return null;
        }
        
        console.log('Final converted chapters data:', {
          count: chaptersData.length,
          firstChapter: chaptersData[0],
          hasValidSections: chaptersData[0]?.sections?.length > 0
        });
        
        // 清理数据，移除缓存相关字段，只保留CourseOutline接口的字段
        const cleanedData: CourseOutline = {
          title: parsedData.title || parsedData.course_title,
          course_title: parsedData.course_title || parsedData.title,
          course_description: parsedData.course_description,
          background_analysis: parsedData.background_analysis,
          bloom_taxonomy_objectives: parsedData.bloom_taxonomy_objectives,
          curriculum_alignment: parsedData.curriculum_alignment,
          chapters: chaptersData
        };
        
        return cleanedData;
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
        
        // 清理数据，移除缓存相关字段，只保留CourseContent接口的字段
        const cleanedData: CourseContent = {
          title: parsedData.title,
          mainContent: parsedData.mainContent,
          keyPoints: parsedData.keyPoints || [],
          images: parsedData.images || [],
          curriculumAlignment: parsedData.curriculumAlignment || []
        };
        
        return cleanedData;
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
        
        // Debug: 检查所有localStorage课程键
        const allKeys = [];
        for(let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if(key && key.startsWith('course_outline_')) {
            allKeys.push(key);
          }
        }
        console.log('All course keys in localStorage:', allKeys);
        
        // 1. 首先检查localStorage缓存
        const cachedOutline = loadCourseFromStorage(initialPrompt);
        if (cachedOutline) {
          console.log('Using cached course outline from localStorage');
          console.log('Cached outline data:', cachedOutline);
          console.log('Cached chapters count:', cachedOutline.chapters?.length || 0);
          
          setOutline(cachedOutline);
          setCourseSource('localStorage');
          setHasCourseGenerated(true); // 确保状态同步
          
          // Select the first section by default
          if (cachedOutline.chapters && cachedOutline.chapters.length > 0) {
            console.log('First chapter:', cachedOutline.chapters[0]);
            console.log('First chapter sections:', cachedOutline.chapters[0].sections);
            if (cachedOutline.chapters[0].sections && cachedOutline.chapters[0].sections.length > 0) {
              console.log('Setting default section:', cachedOutline.chapters[0].sections[0].id);
              setSelectedSection(cachedOutline.chapters[0].sections[0].id);
            } else {
              console.warn('No sections found in first chapter of cached outline');
            }
          } else {
            console.warn('No chapters found in cached outline');
          }
          setIsLoadingOutline(false);
          return;
        }

        // 2. 检查后端是否已有课程
        const existsResult = await checkCourseExists(initialPrompt);
        if (existsResult.exists) {
          console.log(`Course found in ${existsResult.source}, using existing course`);
          console.log('API course data:', existsResult.course_data);
          const courseData = existsResult.course_data;
          
          // 验证和清理数据 - 支持新旧格式和数据结构转换
          let chaptersData = [];
          
          // 处理数据结构：如果是sections格式，转换为chapters格式
          if (Array.isArray(courseData?.sections)) {
            console.log('Converting sections to chapters format');
            chaptersData = courseData.sections.map((section, index) => ({
              id: section?.id || `chapter-${index + 1}`,
              title: section?.title || `第${index + 1}章`,
              description: section?.description || '',
              estimated_duration: section?.estimated_duration,
              bloom_focus: section?.bloom_focus,
              learning_objectives: section?.learning_objectives,
              key_concepts: section?.key_points || section?.key_concepts,
              teaching_resources: section?.teaching_resources,
              content_design_guidance: section?.content_design_guidance,
              curriculum_alignment: section?.curriculum_alignment,
              sections: Array.isArray(section?.subsections) ? section.subsections.map((subsection, subIndex) => ({
                id: subsection?.id || `${section?.id || (index + 1)}.${subIndex + 1}`,
                title: subsection?.title || `第${subIndex + 1}节`,
                content_type: subsection?.content_type,
                activity_suggestion: subsection?.activity_suggestion
              })) : [
                {
                  id: `${section?.id || (index + 1)}.1`,
                  title: `${section?.title || `第${index + 1}章`} - 详细内容`
                }
              ]
            }));
          } else if (Array.isArray(courseData?.chapters)) {
            console.log('Using existing chapters format');
            chaptersData = courseData.chapters;
          }
          
          const validatedData: CourseOutline = {
            // 处理标题 - 支持新格式(course_title)和旧格式(title)
            title: courseData?.course_title || courseData?.title || `${initialPrompt} 课程大纲`,
            course_title: courseData?.course_title || courseData?.title || `${initialPrompt} 课程大纲`,
            course_description: courseData?.course_description,
            background_analysis: courseData?.background_analysis,
            bloom_taxonomy_objectives: courseData?.bloom_taxonomy_objectives,
            curriculum_alignment: courseData?.curriculum_alignment,
            chapters: chaptersData
          };
          
          console.log('Raw data type:', Array.isArray(courseData?.sections) ? 'sections' : 'chapters');
          console.log('Converted chapters count:', validatedData.chapters.length);
          
          // 确保每个章节都有必要的属性
          validatedData.chapters = validatedData.chapters.map((chapter, index) => ({
            id: chapter?.id || `chapter-${index + 1}`,
            title: chapter?.title || `第${index + 1}章`,
            description: chapter?.description || '',
            estimated_duration: chapter?.estimated_duration,
            bloom_focus: chapter?.bloom_focus,
            learning_objectives: chapter?.learning_objectives,
            key_concepts: chapter?.key_concepts,
            teaching_resources: chapter?.teaching_resources,
            content_design_guidance: chapter?.content_design_guidance,
            curriculum_alignment: chapter?.curriculum_alignment,
            sections: Array.isArray(chapter?.sections) ? chapter.sections.map((section, sectionIndex) => ({
              id: section?.id || `${chapter?.id || (index + 1)}.${sectionIndex + 1}`,
              title: section?.title || `第${sectionIndex + 1}节`,
              content_type: section?.content_type,
              activity_suggestion: section?.activity_suggestion
            })) : [
              {
                id: `${chapter?.id || (index + 1)}.1`,
                title: `${chapter?.title || `第${index + 1}章`} - 详细内容`
              }
            ]
          }));

          console.log('Final validated data:', validatedData);
          console.log('Final chapters count:', validatedData.chapters.length);
          
          setOutline(validatedData);
          setCourseSource(existsResult.source);
          setHasCourseGenerated(true); // 确保状态同步
          
          // 保存到localStorage
          saveCourseToStorage(initialPrompt, validatedData);
          
          // Select the first section by default
          if (validatedData.chapters.length > 0 && validatedData.chapters[0].sections.length > 0) {
            console.log('Setting default section from API:', validatedData.chapters[0].sections[0].id);
            setSelectedSection(validatedData.chapters[0].sections[0].id);
          } else {
            console.warn('No sections found in API course data');
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
        
        // 验证和清理数据 - 支持新旧格式和数据结构转换
        let chaptersData = [];
        
        // 处理数据结构：如果是sections格式，转换为chapters格式
        if (Array.isArray(data?.sections)) {
          console.log('Converting new course sections to chapters format');
          chaptersData = data.sections.map((section, index) => ({
            id: section?.id || `chapter-${index + 1}`,
            title: section?.title || `第${index + 1}章`,
            description: section?.description || '',
            estimated_duration: section?.estimated_duration,
            bloom_focus: section?.bloom_focus,
            learning_objectives: section?.learning_objectives,
            key_concepts: section?.key_points || section?.key_concepts,
            teaching_resources: section?.teaching_resources,
            content_design_guidance: section?.content_design_guidance,
            curriculum_alignment: section?.curriculum_alignment,
            sections: Array.isArray(section?.subsections) ? section.subsections.map((subsection, subIndex) => ({
              id: subsection?.id || `${section?.id || (index + 1)}.${subIndex + 1}`,
              title: subsection?.title || `第${subIndex + 1}节`,
              content_type: subsection?.content_type,
              activity_suggestion: subsection?.activity_suggestion
            })) : [
              {
                id: `${section?.id || (index + 1)}.1`,
                title: `${section?.title || `第${index + 1}章`} - 详细内容`
              }
            ]
          }));
        } else if (Array.isArray(data?.chapters)) {
          console.log('Using existing new course chapters format');
          chaptersData = data.chapters;
        }
        
        const validatedData: CourseOutline = {
          // 处理标题 - 支持新格式(course_title)和旧格式(title)
          title: data?.course_title || data?.title || `${initialPrompt} 课程大纲`,
          course_title: data?.course_title || data?.title || `${initialPrompt} 课程大纲`,
          course_description: data?.course_description,
          background_analysis: data?.background_analysis,
          bloom_taxonomy_objectives: data?.bloom_taxonomy_objectives,
          curriculum_alignment: data?.curriculum_alignment,
          chapters: chaptersData
        };
        
        console.log('New course data type:', Array.isArray(data?.sections) ? 'sections' : 'chapters');
        console.log('New course chapters count:', validatedData.chapters.length);
        
        // 确保每个章节都有必要的属性
        validatedData.chapters = validatedData.chapters.map((chapter, index) => ({
          id: chapter?.id || `chapter-${index + 1}`,
          title: chapter?.title || `第${index + 1}章`,
          description: chapter?.description || '',
          estimated_duration: chapter?.estimated_duration,
          bloom_focus: chapter?.bloom_focus,
          learning_objectives: chapter?.learning_objectives,
          key_concepts: chapter?.key_concepts,
          teaching_resources: chapter?.teaching_resources,
          content_design_guidance: chapter?.content_design_guidance,
          curriculum_alignment: chapter?.curriculum_alignment,
          sections: Array.isArray(chapter?.sections) ? chapter.sections.map((section, sectionIndex) => ({
            id: section?.id || `${chapter?.id || (index + 1)}.${sectionIndex + 1}`,
            title: section?.title || `第${sectionIndex + 1}节`,
            content_type: section?.content_type,
            activity_suggestion: section?.activity_suggestion
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
        setHasCourseGenerated(true); // 确保状态同步
        
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
      if (!selectedSection || !initialPrompt) {
        console.log('Skipping section content fetch - missing data:', { selectedSection, initialPrompt });
        return;
      }

      console.log('Fetching section content for:', { selectedSection, initialPrompt });

      try {
        setIsLoadingContent(true);
        
        // 1. 首先检查localStorage缓存
        const cachedContent = loadSectionFromStorage(initialPrompt, selectedSection);
        if (cachedContent) {
          console.log('Using cached section content from localStorage');
          console.log('Cached content:', cachedContent);
          setContent(cachedContent);
          setIsLoadingContent(false);
          return;
        }

        // 2. 如果没有缓存，从API获取
        console.log('Fetching section content from API');
        const data = await getCourseContent(selectedSection, initialPrompt);
        console.log('API section content response:', data);
        setContent(data);
        
        // 保存到localStorage
        saveSectionToStorage(initialPrompt, selectedSection, data);
        console.log('Section content saved to localStorage');
        
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

  // 临时调试函数 - 清理localStorage缓存
  const clearCourseCache = () => {
    const keys = [];
    for(let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if(key && (key.startsWith('course_outline_') || key.startsWith('course_section_'))) {
        keys.push(key);
      }
    }
    keys.forEach(key => localStorage.removeItem(key));
    console.log('Cleared course cache keys:', keys);
    toast.info(`已清理 ${keys.length} 个缓存项`);
    window.location.reload();
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      
      <main className="flex-grow flex">
        {/* Left sidebar - Course overview and navigation (fixed width, scrollable) */}
        <div className="w-80 bg-white shadow-lg border-r border-gray-200 flex flex-col h-[calc(100vh-4rem)]">
          
          {/* Course Overview Section - Fixed at top */}
          <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="flex items-start justify-between mb-3">
              <h2 className="text-lg font-bold text-gray-900 font-display">课程概览</h2>
              <div className="flex gap-2">
                {courseSource && (
                  <div className="text-xs text-gray-500 bg-white px-2 py-1 rounded-full">
                    {courseSource === 'localStorage' && '📱 缓存'}
                    {courseSource === 'memory' && '🧠 记忆'}
                    {courseSource === 'file' && '📄 文件'}
                    {courseSource === 'api' && '🆕 新建'}
                    {courseSource === 'fallback' && '⚠️ 默认'}
                  </div>
                )}
                {/* 临时调试按钮 */}
                <button 
                  onClick={clearCourseCache}
                  className="text-xs text-red-500 hover:text-red-700 px-2 py-1 bg-red-50 hover:bg-red-100 rounded-full transition-colors"
                  title="清理缓存 (调试用)"
                >
                  🗑️
                </button>
              </div>
            </div>
            
            {isLoadingOutline ? (
              <LoadingPlaceholder lines={4} />
            ) : outline ? (
              <div>
                <h3 className="text-base font-semibold text-gray-800 mb-2 leading-tight">
                  {outline.title || outline.course_title}
                </h3>
                
                {outline.course_description && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-3">{outline.course_description}</p>
                )}
                
                {outline.background_analysis && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {outline.background_analysis.target_age && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-700">
                        👥 {outline.background_analysis.target_age}
                      </span>
                    )}
                    {outline.background_analysis.knowledge_level && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-700">
                        📚 {outline.background_analysis.knowledge_level}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">加载中...</p>
            )}
          </div>

          {/* Learning Objectives Section - Collapsible */}
          {outline?.bloom_taxonomy_objectives && (
            <div className="p-4 bg-purple-25">
              <details className="group">
                <summary className="cursor-pointer text-sm font-medium text-purple-800 mb-2 list-none flex items-center justify-between">
                  <span>🎯 学习目标 (布鲁姆分类)</span>
                  <svg className="w-4 h-4 transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </summary>
                <div className="mt-2 space-y-1 text-xs text-purple-700">
                  {Object.entries(outline.bloom_taxonomy_objectives).map(([level, objectives]) => (
                    objectives && objectives.length > 0 && (
                      <div key={level} className="flex">
                        <span className="font-medium capitalize w-16 flex-shrink-0">{level}:</span>
                        <span className="flex-1">{objectives.slice(0, 1).join('、')}
                          {objectives.length > 1 && `等${objectives.length}项`}
                        </span>
                      </div>
                    )
                  ))}
                </div>
              </details>
            </div>
          )}

          {/* 固定的课程章节标题 - 毛玻璃效果，最高 Z-index，紧贴学习目标区域 */}
          <div className="sticky top-0 z-50 backdrop-blur-md bg-white/90 border-t border-gray-200/60 shadow-sm">
            <h4 className="text-sm font-medium text-gray-900 px-4 py-3 flex items-center space-x-2">
              <span>📖 课程章节</span>
              {outline?.chapters && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-blue-100 text-blue-700 ml-auto">
                  {outline.chapters.length}章
                </span>
              )}
            </h4>
          </div>

          {/* Course Navigation - Scrollable */}
          <div className="flex-1 overflow-y-auto px-4 pb-4">
            {isLoadingOutline ? (
              <LoadingPlaceholder lines={8} />
            ) : outline && outline.chapters ? (
              <div className="space-y-3">
                {outline.chapters.map((chapter, chapterIndex) => (
                  <div key={chapter.id} className="space-y-2">
                    {/* Chapter header */}
                    <div className="bg-gray-50 p-3 rounded-lg border border-gray-100 hover:bg-gray-100 transition-colors">
                      <h5 className="font-medium text-gray-900 text-sm mb-1">{chapter.title}</h5>
                      {chapter.description && (
                        <p className="text-xs text-gray-600 mb-2 line-clamp-2">{chapter.description}</p>
                      )}
                      
                      <div className="flex flex-wrap gap-1 mb-2">
                        {chapter.estimated_duration && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-100 text-blue-700">
                            ⏱️ {chapter.estimated_duration}
                          </span>
                        )}
                        {chapter.bloom_focus && chapter.bloom_focus.length > 0 && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-purple-100 text-purple-700">
                            🎯 {chapter.bloom_focus.slice(0, 2).join('、')}
                          </span>
                        )}
                      </div>
                      
                      {chapter.key_concepts && chapter.key_concepts.length > 0 && (
                        <div className="text-xs text-gray-600">
                          <span className="font-medium">核心概念:</span> {chapter.key_concepts.slice(0, 2).join('、')}
                          {chapter.key_concepts.length > 2 && '...'}
                        </div>
                      )}
                    </div>

                    {/* Chapter sections */}
                    <div className="ml-4 space-y-1">
                      {chapter.sections && chapter.sections.length > 0 ? (
                        chapter.sections.map((section, sectionIndex) => (
                          <button
                            key={section.id}
                            onClick={() => setSelectedSection(section.id)}
                            className={`text-left w-full p-2 text-sm rounded-lg border transition-all duration-200 relative ${
                              selectedSection === section.id
                                ? 'bg-primary text-white border-primary shadow-md z-10'
                                : 'text-gray-700 border-gray-200 hover:bg-gray-50 hover:border-gray-300 z-0'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-medium">{chapterIndex + 1}.{sectionIndex + 1} {section.title}</span>
                              {selectedSection === section.id && (
                                <svg className="w-4 h-4 ml-2" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                </svg>
                              )}
                            </div>
                            {section.content_type && (
                              <div className="text-xs text-gray-500 mt-1">
                                📄 {section.content_type}
                              </div>
                            )}
                          </button>
                        ))
                      ) : (
                        <div className="text-sm text-gray-500 p-2 italic">暂无章节内容</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 text-sm">暂无课程章节</div>
            )}
          </div>

          {/* Action buttons - Fixed at bottom */}
          <div className="p-4 border-t border-gray-100 bg-white">
            <Button onClick={handleStartLearning} className="w-full" size="sm">
              🚀 开始互动学习
            </Button>
          </div>
        </div>
        
        {/* Right area - Detailed content */}
        <div className="flex-1 flex flex-col h-[calc(100vh-4rem)]">
          
          {/* Content header - Fixed */}
          <div className="bg-white border-b border-gray-200 px-8 py-4 shadow-sm">
            {selectedSection && content ? (
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 font-display">{content.title}</h2>
                  <p className="text-sm text-gray-600 mt-1">当前学习章节</p>
                </div>
                <Button onClick={handleStartLearning} size="sm" variant="outline">
                  开始练习
                </Button>
              </div>
            ) : (
              <div>
                <h2 className="text-xl font-bold text-gray-900 font-display">课程内容</h2>
                <p className="text-sm text-gray-600 mt-1">请从左侧选择要学习的章节</p>
              </div>
            )}
          </div>

          {/* Content body - Scrollable */}
          <div className="flex-1 overflow-y-auto p-8 bg-gray-50">
            {isLoadingContent ? (
              <div className="max-w-4xl mx-auto space-y-8">
                <LoadingPlaceholder type="image" />
                <LoadingPlaceholder lines={8} />
                <LoadingPlaceholder lines={3} />
              </div>
            ) : content ? (
              <div className="max-w-4xl mx-auto space-y-8">
                
                {/* Images section */}
                {content.images && content.images.length > 0 && (
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center">
                      🖼️ 图片资源
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {content.images.map((image, index) => (
                        <figure key={index} className="rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow">
                          <img 
                            src={image.url} 
                            alt={image.caption} 
                            className="w-full h-48 object-cover"
                          />
                          <figcaption className="p-3 text-sm text-gray-700 bg-gray-50">
                            {image.caption}
                          </figcaption>
                        </figure>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Main content */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center">
                    📚 主要内容
                  </h3>
                  <div className="prose prose-gray max-w-none">
                    <MarkdownRenderer content={content.mainContent} />
                  </div>
                </div>
                
                {/* Key points */}
                {content.keyPoints && content.keyPoints.length > 0 && (
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center">
                      🎯 核心知识点
                    </h3>
                    <div className="grid gap-3">
                      {content.keyPoints.map((point, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
                          <div className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                            {index + 1}
                          </div>
                          <p className="text-gray-800 flex-1">{point}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Curriculum alignment */}
                {content.curriculumAlignment && content.curriculumAlignment.length > 0 && (
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center">
                      📋 课标对齐
                    </h3>
                    <div className="space-y-2">
                      {content.curriculumAlignment.map((alignment, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg border border-green-100">
                          <div className="flex-shrink-0 w-5 h-5 text-green-600 mt-0.5">
                            <svg fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                          <p className="text-gray-800 flex-1">{alignment}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Call to action */}
                <div className="text-center bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-8 text-white">
                  <h3 className="text-xl font-bold mb-2">准备好开始学习了吗？</h3>
                  <p className="text-blue-100 mb-4">开启您的互动学习之旅</p>
                  <Button onClick={handleStartLearning} size="lg" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100">
                    🚀 开始互动学习
                  </Button>
                </div>

              </div>
            ) : selectedSection ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">正在加载内容...</h3>
                <p className="text-gray-500">请稍候，我们正在为您准备学习资料</p>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">选择一个章节开始学习</h3>
                <p className="text-gray-500 max-w-md">
                  从左侧课程导航中选择您想要学习的章节，我们将为您展示详细的学习内容和教学资源
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default CoursePlanning;
