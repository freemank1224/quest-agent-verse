import { getCourseContent } from '@/services/api';

export interface CourseCompleteness {
  total_sections: number;
  cached_sections: number;
  complete_outline: boolean;
  status: 'complete' | 'incomplete_content' | 'incomplete_outline' | 'empty';
  missing_sections: string[];
  cached_section_ids: string[];
}

export interface Section {
  id: string;
  title: string;
  content_type?: string;
}

export interface Chapter {
  id: string;
  title: string;
  description?: string;
  sections: Section[];
}

export interface CourseOutline {
  course_title?: string;
  course_description?: string;
  title?: string;
  chapters: Chapter[];
}

/**
 * 检查章节是否有缓存内容
 */
export const checkSectionCached = (topic: string, sectionId: string): boolean => {
  if (!topic || !sectionId) return false;
  try {
    const storageKey = `course_section_${topic.replace(/\s+/g, '_')}_${sectionId}`;
    return localStorage.getItem(storageKey) !== null;
  } catch {
    return false;
  }
};

/**
 * 分析课程完整性
 */
export const analyzeCourseCompleteness = (
  topic: string, 
  courseOutline: CourseOutline
): CourseCompleteness => {
  if (!courseOutline || !courseOutline.chapters || courseOutline.chapters.length === 0) {
    return {
      total_sections: 0,
      cached_sections: 0,
      complete_outline: false,
      status: 'incomplete_outline',
      missing_sections: [],
      cached_section_ids: []
    };
  }

  // 收集所有章节
  const allSections: Section[] = [];
  courseOutline.chapters.forEach(chapter => {
    if (chapter.sections && Array.isArray(chapter.sections)) {
      allSections.push(...chapter.sections);
    }
  });

  if (allSections.length === 0) {
    return {
      total_sections: 0,
      cached_sections: 0,
      complete_outline: false,
      status: 'incomplete_outline',
      missing_sections: [],
      cached_section_ids: []
    };
  }

  // 检查每个章节的缓存状态
  const cachedSectionIds: string[] = [];
  const missingSections: string[] = [];

  allSections.forEach(section => {
    if (checkSectionCached(topic, section.id)) {
      cachedSectionIds.push(section.id);
    } else {
      missingSections.push(section.id);
    }
  });

  const totalSections = allSections.length;
  const cachedSections = cachedSectionIds.length;
  const completeOutline = true; // 如果走到这里，说明大纲是完整的

  let status: CourseCompleteness['status'];
  if (cachedSections === totalSections) {
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
    status,
    missing_sections: missingSections,
    cached_section_ids: cachedSectionIds
  };
};

/**
 * 检查课程是否需要重新生成大纲
 */
export const shouldRegenerateOutline = (completeness: CourseCompleteness): boolean => {
  return completeness.status === 'incomplete_outline' || 
         (!completeness.complete_outline);
};

/**
 * 检查课程是否需要补充内容
 */
export const needsContentGeneration = (completeness: CourseCompleteness): boolean => {
  return completeness.status === 'incomplete_content' || 
         completeness.status === 'empty';
};

/**
 * 获取缺失的章节列表（用于显示和生成）
 */
export const getMissingSections = (
  courseOutline: CourseOutline, 
  completeness: CourseCompleteness
): Section[] => {
  const allSections: Section[] = [];
  courseOutline.chapters.forEach(chapter => {
    if (chapter.sections && Array.isArray(chapter.sections)) {
      chapter.sections.forEach(section => {
        if (completeness.missing_sections.includes(section.id)) {
          allSections.push(section);
        }
      });
    }
  });
  return allSections;
};

/**
 * 生成缺失章节的内容
 */
export const generateMissingSectionContent = async (
  topic: string,
  sectionId: string,
  onProgress?: (sectionId: string, status: 'loading' | 'success' | 'error') => void
): Promise<boolean> => {
  try {
    onProgress?.(sectionId, 'loading');
    
    const content = await getCourseContent(sectionId, topic);
    
    // 保存到localStorage
    const storageKey = `course_section_${topic.replace(/\s+/g, '_')}_${sectionId}`;
    const dataToStore = {
      ...content,
      cachedAt: new Date().toISOString(),
      topic: topic,
      sectionId: sectionId
    };
    localStorage.setItem(storageKey, JSON.stringify(dataToStore));
    
    onProgress?.(sectionId, 'success');
    return true;
  } catch (error) {
    console.error(`Error generating content for section ${sectionId}:`, error);
    onProgress?.(sectionId, 'error');
    return false;
  }
};

/**
 * 批量生成缺失章节内容
 */
export const generateAllMissingContent = async (
  topic: string,
  missingSectionIds: string[],
  onProgress?: (sectionId: string, status: 'loading' | 'success' | 'error') => void,
  onComplete?: (successful: number, failed: number) => void
): Promise<void> => {
  let successful = 0;
  let failed = 0;

  // 逐个生成，避免并发过多
  for (const sectionId of missingSectionIds) {
    const success = await generateMissingSectionContent(topic, sectionId, onProgress);
    if (success) {
      successful++;
    } else {
      failed++;
    }
    
    // 添加小延迟避免请求过快
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  onComplete?.(successful, failed);
};

/**
 * 格式化课程状态显示
 */
export const formatCourseStatus = (completeness: CourseCompleteness) => {
  switch (completeness.status) {
    case 'complete':
      return {
        text: '完整课程',
        color: 'green',
        description: '所有内容已生成，可直接开始学习'
      };
    case 'incomplete_content':
      return {
        text: '部分内容',
        color: 'yellow',
        description: `${completeness.cached_sections}/${completeness.total_sections} 章节已生成，需补充剩余内容`
      };
    case 'incomplete_outline':
      return {
        text: '大纲不完整',
        color: 'orange',
        description: '课程大纲结构不完整，建议重新生成'
      };
    case 'empty':
      return {
        text: '空课程',
        color: 'red',
        description: '课程大纲完整，但尚未生成任何章节内容'
      };
    default:
      return {
        text: '未知状态',
        color: 'gray',
        description: '无法确定课程状态'
      };
  }
};
