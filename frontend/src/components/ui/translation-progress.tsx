"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Progress } from "./progress"
import { Loader2, FileText, Image } from "lucide-react"

interface TranslationProgressProps {
  progress: number
  currentPage?: number
  totalPages?: number
  message?: string
  isProcessing?: boolean
  isPdf?: boolean
}

export function TranslationProgress({
  progress,
  currentPage = 0,
  totalPages = 0,
  message = "Processing...",
  isProcessing = true,
  isPdf = false
}: TranslationProgressProps) {
  return (
    <motion.div 
      className="flex flex-col items-center justify-center min-h-[350px] w-full p-6"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Icon */}
      <motion.div
        animate={{ rotate: isProcessing ? 360 : 0 }}
        transition={{ duration: 2, repeat: isProcessing ? Infinity : 0, ease: "linear" }}
        className="mb-6"
      >
        {isPdf ? (
          <FileText className="h-12 w-12 text-primary" />
        ) : (
          <Image className="h-12 w-12 text-primary" />
        )}
      </motion.div>

      {/* Main message */}
      <motion.div 
        className="text-lg font-semibold text-foreground mb-2 text-center"
        key={message}
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {isProcessing ? "Translating…" : "Translation Complete!"}
      </motion.div>

      {/* Progress bar */}
      <div className="w-full max-w-md mb-4">
        <Progress value={progress} className="h-3" />
      </div>

      {/* Progress details */}
      <motion.div 
        className="flex flex-col items-center space-y-2 text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        {/* Progress percentage */}
        <div className="text-sm font-medium text-foreground">
          {Math.round(progress)}%
        </div>

        {/* Page progress for PDFs */}
        {isPdf && totalPages > 0 && (
          <motion.div 
            className="text-sm text-muted-foreground"
            key={`${currentPage}-${totalPages}`}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
          >
            Page {currentPage} of {totalPages}
          </motion.div>
        )}

        {/* Status message */}
        <motion.div 
          className="text-xs text-muted-foreground max-w-sm leading-relaxed"
          key={message}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {message}
        </motion.div>

        {/* Loading indicator */}
        {isProcessing && (
          <motion.div
            className="flex items-center space-x-2 text-xs text-muted-foreground mt-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <Loader2 className="h-3 w-3 animate-spin" />
            <span>Please do not close this window</span>
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  )
} 