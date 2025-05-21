
import React from 'react';
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

interface ImagePanelProps {
  isImagePanelOpen: boolean;
  setIsImagePanelOpen: React.Dispatch<React.SetStateAction<boolean>>;
  imageUrl: string;
}

const ImagePanel: React.FC<ImagePanelProps> = ({ 
  isImagePanelOpen, 
  setIsImagePanelOpen, 
  imageUrl 
}) => {
  return (
    <Collapsible
      open={isImagePanelOpen}
      onOpenChange={setIsImagePanelOpen}
      className="w-full"
    >
      <div className="sticky top-0 z-10 backdrop-blur-lg bg-white/60 shadow-sm border-b border-gray-200">
        <CollapsibleContent>
          <div className="p-3">
            <div className="aspect-[2/1] bg-gray-50 rounded-lg overflow-hidden border border-gray-100">
              <img
                src={imageUrl}
                alt="学习相关图片"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </CollapsibleContent>
        <div className="flex justify-end">
          <CollapsibleTrigger asChild>
            <Button 
              variant="ghost" 
              size="sm"
              className="absolute bottom-0 right-4 transform translate-y-1/2 rounded-full w-10 h-10 p-0 bg-white shadow-md hover:bg-gray-100 border border-gray-100 flex items-center justify-center"
              style={{
                boxShadow: '0 4px 10px rgba(0, 0, 0, 0.08)',
                zIndex: 20
              }}
            >
              {isImagePanelOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </Button>
          </CollapsibleTrigger>
        </div>
      </div>
    </Collapsible>
  );
};

export default ImagePanel;
