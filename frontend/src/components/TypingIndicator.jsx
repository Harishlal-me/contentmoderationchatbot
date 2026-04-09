import React from 'react';
import { motion } from 'framer-motion';

export default function TypingIndicator() {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex justify-start w-full"
    >
      <div className="bg-white/5 border border-white/10 backdrop-blur-md rounded-2xl py-3 px-4 flex items-center shadow-sm w-fit">
        <div className="flex gap-1.5 items-center justify-center">
          <span 
            className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce" 
            style={{ animationDelay: '0ms', animationDuration: '0.8s' }} 
          />
          <span 
            className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce" 
            style={{ animationDelay: '150ms', animationDuration: '0.8s' }} 
          />
          <span 
            className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce" 
            style={{ animationDelay: '300ms', animationDuration: '0.8s' }} 
          />
        </div>
      </div>
    </motion.div>
  );
}
