
import React from 'react';
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, ChevronLeft, ChevronRight } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

interface ImagePanelProps {
  isImagePanelOpen: boolean;
  setIsImagePanelOpen: React.Dispatch<React.SetStateAction<boolean>>;
  imageUrl: string;
  onPreviousImage?: () => void;
  onNextImage?: () => void;
  hasMultipleImages?: boolean;
  currentImageIndex?: number;
  totalImages?: number;
}

const ImagePanel: React.FC<ImagePanelProps> = ({ 
  isImagePanelOpen, 
  setIsImagePanelOpen, 
  imageUrl,
  onPreviousImage,
  onNextImage,
  hasMultipleImages = false,
  currentImageIndex = 0,
  totalImages = 1
}) => {
  return (
    <Collapsible
      open={isImagePanelOpen}
      onOpenChange={setIsImagePanelOpen}
      className="w-full"
    >
      <div className="sticky top-0 z-10 glass-effect shadow-sm border-b border-gray-200/50">
        <CollapsibleContent>
          <div className="p-3">
            <div className="relative aspect-[2/1] bg-gray-50/70 rounded-lg overflow-hidden border border-gray-100/50">
              <img
                src={imageUrl}
                alt="学习相关图片"
                className="w-full h-full object-cover"
                onError={(e) => {
                  // 如果图片加载失败，显示占位符
                  const target = e.target as HTMLImageElement;
                  target.src = '/placeholder.svg';
                }}
              />
              
              {/* 图片切换按钮 */}
              {hasMultipleImages && totalImages > 1 && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onPreviousImage}
                    className="absolute left-2 top-1/2 transform -translate-y-1/2 rounded-full w-8 h-8 p-0 glass-effect hover:bg-white/70 flex items-center justify-center"
                    style={{
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                    }}
                  >
                    <ChevronLeft size={14} />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onNextImage}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 rounded-full w-8 h-8 p-0 glass-effect hover:bg-white/70 flex items-center justify-center"
                    style={{
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                    }}
                  >
                    <ChevronRight size={14} />
                  </Button>
                  
                  {/* 图片指示器 */}
                  <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
                    {Array.from({ length: totalImages }).map((_, index) => (
                      <div
                        key={index}
                        className={`w-2 h-2 rounded-full ${
                          index === currentImageIndex 
                            ? 'bg-white' 
                            : 'bg-white/50'
                        }`}
                        style={{
                          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.3)',
                        }}
                      />
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </CollapsibleContent>
        <div className="flex justify-end">
          <CollapsibleTrigger asChild>
            <Button 
              variant="ghost" 
              size="sm"
              className="absolute bottom-0 right-4 transform translate-y-1/2 rounded-full w-10 h-10 p-0 glass-effect hover:bg-white/70 flex items-center justify-center"
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
