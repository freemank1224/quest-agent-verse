// 实际API调用，连接到后端
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api';

// 辅助函数，检测API响应状态
async function checkResponse(response: Response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.message || `API错误：${response.status} ${response.statusText}`
    );
  }
  return response.json();
}

// 建立WebSocket连接
export const connectWebSocket = (
  clientId: string,
  onMessage: (data: any) => void,
  onClose: () => void
) => {
  const socket = new WebSocket(`${WS_URL}/ws/chat/${clientId}`);
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  
  socket.onclose = () => {
    onClose();
  };
  
  return {
    send: (content: string, sender: string) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ content, sender }));
      }
    },
    close: () => socket.close()
  };
};

// 发送查询到Agent
export const sendQueryToAgent = async (query: string): Promise<string> => {
  console.log('Sending query to agent:', query);
  
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
    
    const data = await checkResponse(response);
    return data.response;
  } catch (error) {
    console.error('Error sending query to agent:', error);
    throw error;
  }
};

// 检查课程是否已存在
export const checkCourseExists = async (topic: string): Promise<any> => {
  console.log('Checking if course exists for topic:', topic);
  
  try {
    const response = await fetch(`${API_URL}/course/exists/${encodeURIComponent(topic)}`);
    return await checkResponse(response);
  } catch (error) {
    console.error('Error checking course existence:', error);
    throw error;
  }
};

// 获取课程大纲
export const getCourseOutline = async (
  topic: string, 
  learningGoal?: string, 
  duration?: string, 
  backgroundLevel?: string
): Promise<any> => {
  console.log('Getting course outline for:', topic);
  
  try {
    const response = await fetch(`${API_URL}/course/plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        topic, 
        learning_goal: learningGoal, 
        duration, 
        background_level: backgroundLevel 
      }),
    });
    
    return await checkResponse(response);
  } catch (error) {
    console.error('Error getting course outline:', error);
    throw error;
  }
};

// 获取课程内容
export const getCourseContent = async (sectionId: string, topic?: string): Promise<any> => {
  console.log('Getting course content for section:', sectionId);
  
  try {
    const url = new URL(`${API_URL}/course/content/${encodeURIComponent(sectionId)}`);
    if (topic) {
      url.searchParams.append('topic', topic);
    }
    
    const response = await fetch(url.toString());
    return await checkResponse(response);
  } catch (error) {
    console.error('Error getting course content:', error);
    throw error;
  }
};

// 获取已存储的课程列表
export const getCourseList = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_URL}/course/list`);
    return await checkResponse(response);
  } catch (error) {
    console.error('Error getting course list:', error);
    throw error;
  }
};

// 获取用户学习进度
export const getUserProgress = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_URL}/user/progress`);
    return await checkResponse(response);
  } catch (error) {
    console.error('Error getting user progress:', error);
    throw error;
  }
};

// 设置教学上下文
export const setTeachingContext = async (clientId: string, topic: string, sessionId?: string): Promise<any> => {
  try {
    const response = await fetch(`${API_URL}/teaching/set-context`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        client_id: clientId,
        topic: topic,
        session_id: sessionId 
      }),
    });
    
    return await checkResponse(response);
  } catch (error) {
    console.error('Error setting teaching context:', error);
    throw error;
  }
};
