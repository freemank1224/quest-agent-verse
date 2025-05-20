
import React from 'react';
import { cn } from '@/lib/utils';

interface LoadingPlaceholderProps {
  type?: 'text' | 'block' | 'image';
  lines?: number;
  className?: string;
}

const LoadingPlaceholder: React.FC<LoadingPlaceholderProps> = ({
  type = 'text',
  lines = 3,
  className,
}) => {
  if (type === 'text') {
    return (
      <div className={cn("space-y-2", className)}>
        {Array.from({ length: lines }).map((_, i) => (
          <div 
            key={i} 
            className={cn(
              "h-4 bg-gray-200 rounded shimmer",
              i === lines - 1 && lines > 1 ? "w-2/3" : "w-full"
            )}
          />
        ))}
      </div>
    );
  }

  if (type === 'image') {
    return (
      <div className={cn("aspect-video bg-gray-200 rounded shimmer", className)} />
    );
  }

  // Block type (default)
  return (
    <div className={cn("h-32 bg-gray-200 rounded shimmer", className)} />
  );
};

export default LoadingPlaceholder;
