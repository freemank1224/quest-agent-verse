
// Simulating API calls for now, as we don't have a real backend yet

// Function to simulate sending a query to the agent
export const sendQueryToAgent = async (query: string): Promise<string> => {
  console.log('Sending query to agent:', query);
  
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Return a mock response
  return `这是对"${query}"的模拟回复。在实际应用中，这将由后端Agent服务提供。`;
};

// Function to simulate getting course outline
export const getCourseOutline = async (topic: string): Promise<any> => {
  console.log('Getting course outline for:', topic);
  
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 2500));
  
  // Return a mock response
  return {
    title: `${topic}学习计划`,
    chapters: [
      {
        id: '1',
        title: '第一章：基础概念',
        sections: [
          { id: '1.1', title: '1.1 核心原理介绍' },
          { id: '1.2', title: '1.2 历史与发展' },
        ]
      },
      {
        id: '2',
        title: '第二章：进阶知识',
        sections: [
          { id: '2.1', title: '2.1 理论应用' },
          { id: '2.2', title: '2.2 实践方法' },
        ]
      },
      {
        id: '3',
        title: '第三章：综合实践',
        sections: [
          { id: '3.1', title: '3.1 案例分析' },
          { id: '3.2', title: '3.2 问题解决' },
        ]
      }
    ]
  };
};

// Function to simulate getting course content
export const getCourseContent = async (sectionId: string): Promise<any> => {
  console.log('Getting course content for section:', sectionId);
  
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Return a mock response
  return {
    title: `章节 ${sectionId}`,
    mainContent: `
# ${sectionId} 主要内容

这是该章节的主要内容。在实际应用中，这将是由Agent生成的详细教学内容。

## 子标题1

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam euismod, nisl eget ultricies ultrices, nunc nisl ultricies nunc, eget ultricies nisl eget ultricies.

## 子标题2

以下是一个数学公式的例子：

$$E = mc^2$$

### 代码示例

\`\`\`python
def hello_world():
    print("Hello, world!")
\`\`\`

### 流程图示例

\`\`\`mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
\`\`\`
    `,
    keyPoints: [
      '核心知识点1：这是一个重要的概念',
      '核心知识点2：这是另一个关键理解',
      '核心知识点3：实践应用方法'
    ],
    images: [
      {
        url: 'https://source.unsplash.com/random/800x600/?education',
        caption: '相关图片资源'
      }
    ],
    curriculumAlignment: [
      '课标要求1：符合XX年级XX学科核心素养要求',
      '课标要求2：培养学生的逻辑思维能力',
      '课标要求3：鼓励学生应用知识解决实际问题'
    ]
  };
};

// Function to simulate getting user progress
export const getUserProgress = async (): Promise<any> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return a mock response
  return {
    completedChapters: ['1', '2'],
    achievements: [
      { id: '1', title: '学习初探', description: '完成第一章学习' },
      { id: '2', title: '学习进阶', description: '完成两个章节学习' }
    ],
    progressPercentage: 60
  };
};
