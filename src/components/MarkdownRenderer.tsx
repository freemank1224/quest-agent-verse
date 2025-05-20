
import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import mermaid from 'mermaid';
import 'katex/dist/katex.min.css';

interface MarkdownRendererProps {
  content: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  const [key, setKey] = useState(0);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
    });
  }, []);

  // Process the content to handle mermaid diagrams
  useEffect(() => {
    const processMermaid = () => {
      const elements = document.querySelectorAll('.mermaid');
      
      if (elements.length > 0) {
        // Type assertion to address TypeScript error
        mermaid.init(undefined, elements as NodeListOf<HTMLElement>);
        // Force a re-render to ensure mermaid diagrams are properly displayed
        setKey(prev => prev + 1);
      }
    };

    processMermaid();
  }, [content]);

  return (
    <div className="markdown-content" key={key}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex, rehypeRaw]}
        components={{
          pre({ node, className, children, ...props }) {
            return (
              <pre className={className} {...props}>
                {children}
              </pre>
            );
          },
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            
            // Handle Mermaid diagrams
            if (match && match[1] === 'mermaid') {
              return (
                <div className="mermaid">{String(children).replace(/\n$/, '')}</div>
              );
            }
            
            // Check if it's an inline code block based on className
            const isInline = !className || !className.includes('language-');
            
            return isInline ? (
              <code className="inline-code" {...props}>
                {children}
              </code>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
