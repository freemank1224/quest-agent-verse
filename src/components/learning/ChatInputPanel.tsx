
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
      <div className="glass-effect rounded-lg shadow-md p-4">
        <ChatInput 
          onSpeakerToggle={onSpeakerToggle}
          isSpeakerOn={isSpeakerOn}
        />
      </div>
    </div>
  );
};

export default ChatInputPanel;
