'use client';

import { motion } from 'framer-motion';
import { BookOpen, Users, Star, ArrowRight, Zap, Sparkles } from 'lucide-react';

export function Hero() {
  const comicImages = [
    'comicbook.png',
    'comicbook.webp',
    'comicbook2.webp', 
    'comicbook3.jpg',
    'translated_comic_c08931ab-736f-498c-881a-5dd28023534b.png',
    'translated_comic_d81f67a6-029d-4cdc-a6eb-9d525c44a0d9.png'
  ];

  // Reduced particles for cleaner look
  const particles = Array.from({ length: 8 }, (_, i) => i);

  return (
    <section className="hero-manga">
      {/* Simplified Background Layers */}
      <div className="hero-bg-simple"></div>
      
      {/* Reduced Particles */}
      <div className="particles-container">
        {particles.map((particle) => (
          <motion.div
            key={particle}
            className="particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -50, 0],
              opacity: [0, 0.6, 0],
              scale: [0, 0.8, 0],
            }}
            transition={{
              duration: Math.random() * 4 + 3,
              repeat: Infinity,
              delay: Math.random() * 3,
            }}
          />
        ))}
      </div>

      {/* Simplified Comic Gallery */}
      <div className="comic-gallery">
        {comicImages.map((image, index) => (
          <motion.div
            key={index}
            className={`floating-comic-${index + 1}`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ 
              opacity: [0.4, 0.6, 0.4],
              y: [0, -15, 0],
            }}
            transition={{
              duration: 5 + index,
              repeat: Infinity,
              delay: index * 0.8,
            }}
            whileHover={{ 
              scale: 1.1, 
              opacity: 0.9,
              zIndex: 100,
            }}
          >
            <div className="comic-frame">
              <img src={`/${image}`} alt={`Comic ${index + 1}`} />
              <div className="comic-glow"></div>
              <div className="comic-border"></div>
            </div>
          </motion.div>
        ))}
      </div>
      
      {/* Hero Content */}
      <div className="hero-content-manga">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          className="hero-text-clean"
        >
          {/* Simplified Title */}
          <motion.div
            className="title-simple"
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="hero-title-clean">
              <span className="gradient-text-simple">COMIC</span>
              <span className="explosion-text">💥</span>
              <span className="gradient-text-simple manga">MANGA</span>
              <div className="subtitle-clean">
                <Zap className="subtitle-icon-simple" />
                AI TRANSLATOR
              </div>
            </h1>
          </motion.div>
          
          {/* Clean Description */}
          <motion.p 
            className="hero-description-clean"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            Translate any comic into <strong>12+ languages</strong> with perfect 
            <strong> context</strong> and <strong>accuracy</strong>
          </motion.p>
          
          {/* Clean CTA Button */}
          <motion.button
            className="cta-button-clean"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.8 }}
            whileHover={{ 
              scale: 1.05,
              boxShadow: "0 15px 35px rgba(255,107,107,0.3)",
            }}
            whileTap={{ scale: 0.95 }}
            onClick={() => window.location.href = 'http://localhost:8080'}
          >
            <span className="button-text">Start Translating</span>
            <ArrowRight className="button-icon-clean" />
          </motion.button>
        </motion.div>
      </div>

      {/* Simplified Action Bubbles */}
      <div className="action-bubbles-simple">
        <motion.div 
          className="bubble-simple pow"
          animate={{ 
            scale: [1, 1.1, 1],
          }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          POW!
        </motion.div>
        <motion.div 
          className="bubble-simple boom"
          animate={{ 
            scale: [1, 1.15, 1],
          }}
          transition={{ duration: 3.5, repeat: Infinity, delay: 1 }}
        >
          BOOM!
        </motion.div>
      </div>
    </section>
  );
} 