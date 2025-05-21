
import React from 'react';
import ChatInput from '@/components/ChatInput';

interface ChatInputPanelProps {
  onSpeakerToggle: () => void;
  isSpeakerOn: boolean;
}

const ChatInputPanel: React.FC<ChatInputPanelProps> = ({ 
  onSpeakerToggle, 
  isSpeakerOn 
}) => {
  return (
    <div className="sticky bottom-4 z-10 mx-4">
      <div className="backdrop-blur-md bg-white/70 rounded-lg shadow-md p-4 border border-gray-100">
        <ChatInput 
          onSpeakerToggle={onSpeakerToggle}
          isSpeakerOn={isSpeakerOn}
        />
      </div>
    </div>
  );
};

export default ChatInputPanel;
