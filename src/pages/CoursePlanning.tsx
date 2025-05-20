
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import Navbar from '@/components/Navbar';
import MarkdownRenderer from '@/components/MarkdownRenderer';
import LoadingPlaceholder from '@/components/LoadingPlaceholder';
import { useChat } from '@/contexts/ChatContext';
import { getCourseOutline, getCourseContent } from '@/services/api';
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
        const data = await getCourseOutline(initialPrompt);
        setOutline(data);
        
        // Select the first section by default
        if (data.chapters.length > 0 && data.chapters[0].sections.length > 0) {
          setSelectedSection(data.chapters[0].sections[0].id);
        }
      } catch (error) {
        console.error('Error fetching course outline:', error);
        toast.error('获取课程大纲失败，请重试');
      } finally {
        setIsLoadingOutline(false);
      }
    };

    fetchCourseOutline();
  }, [initialPrompt, navigate]);

  useEffect(() => {
    const fetchSectionContent = async () => {
      if (!selectedSection) return;

      try {
        setIsLoadingContent(true);
        const data = await getCourseContent(selectedSection);
        setContent(data);
      } catch (error) {
        console.error('Error fetching section content:', error);
        toast.error('获取章节内容失败，请重试');
      } finally {
        setIsLoadingContent(false);
      }
    };

    fetchSectionContent();
  }, [selectedSection]);

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
          
          {isLoadingOutline ? (
            <LoadingPlaceholder lines={10} />
          ) : outline ? (
            <div>
              <h3 className="text-lg font-semibold mb-2">{outline.title}</h3>
              <div className="space-y-4 mt-4">
                {outline.chapters.map((chapter) => (
                  <div key={chapter.id} className="space-y-2">
                    <h4 className="font-medium text-gray-900">{chapter.title}</h4>
                    <ul className="ml-4 space-y-1">
                      {chapter.sections.map((section) => (
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
                      ))}
                    </ul>
                  </div>
                ))}
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
