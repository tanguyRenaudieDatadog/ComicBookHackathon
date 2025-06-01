'use client';

import { motion } from 'framer-motion';
import { BookOpen, Sparkles, ArrowRight } from 'lucide-react';

export function HowItWorks() {
  const showcaseExamples = [
    {
      image: 'comicbook.webp',
      category: 'Asian Literature',
      title: 'Japanese Manga',
      subtitle: 'Traditional storytelling with cultural depth',
      highlights: [
        { icon: '📖', text: 'Right-to-left reading flow' },
        { icon: '🗾', text: 'Cultural expressions & honorifics' },
        { icon: '🎭', text: 'Authentic character voices' }
      ],
      badge: '🎌 Authentic'
    },
    {
      image: 'comicbook2.webp',
      category: 'Western Comics',
      title: 'US Superhero Comics',
      subtitle: 'High-energy action and heroic narratives',
      highlights: [
        { icon: '💥', text: 'Dynamic action sequences' },
        { icon: '🦸', text: 'Hero dialogue & monologues' },
        { icon: '⚡', text: 'Explosive sound effects' }
      ],
      badge: '💥 Dynamic'
    },
    {
      image: 'comicbook3.jpg',
      category: 'Educational Content',
      title: 'Technical Manuals',
      subtitle: 'Precise instructions and professional guides',
      highlights: [
        { icon: '📋', text: 'Step-by-step instructions' },
        { icon: '🔧', text: 'Technical terminology' },
        { icon: '📊', text: 'Professional documentation' }
      ],
      badge: '🔧 Precise'
    }
  ];

  return (
    <>
      {/* Comic Showcase */}
      <section id="showcase" className="showcase">
        <div className="container">
          <h2 className="section-title">
            <BookOpen className="title-icon" />
            Translation Examples
          </h2>
          <p className="section-subtitle showcase-subtitle">
            See how our AI transforms different types of content while preserving their unique characteristics
          </p>
          
          <div className="comics-showcase">
            {showcaseExamples.map((example, index) => (
              <motion.div
                key={index}
                className="showcase-card-new"
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="showcase-image-container">
                  <img src={`/${example.image}`} alt={`${example.title} Example`} />
                  <div className="showcase-overlay-new">
                    <div className="showcase-content-new">
                      
                      {/* Header Section */}
                      <div className="showcase-header-new">
                        <span className="showcase-category-new">{example.category}</span>
                        <h3 className="showcase-title-new">{example.title}</h3>
                        <p className="showcase-subtitle-new">{example.subtitle}</p>
                      </div>

                      {/* Highlights Section */}
                      <div className="showcase-highlights">
                        {example.highlights.map((highlight, idx) => (
                          <div key={idx} className="highlight-item">
                            <span className="highlight-icon">{highlight.icon}</span>
                            <span className="highlight-text">{highlight.text}</span>
                          </div>
                        ))}
                      </div>

                      {/* Badge */}
                      <div className="showcase-badge-new">
                        <span>{example.badge}</span>
                      </div>

                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-grid">
            {/* Main CTA Section */}
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              className="footer-main"
            >
              <h3>Ready to Explore Stories in Any Language?</h3>
              <p>Join thousands of readers discovering amazing comics and manga from around the world!</p>
              <motion.button
                className="cta-button footer-cta"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => window.location.href = 'http://localhost:8080'}
              >
                Get Started Now <ArrowRight className="button-icon" />
              </motion.button>
            </motion.div>

            {/* Stats Section */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="footer-stats"
            >
              <div className="footer-stat">
                <span className="stat-number">1000+</span>
                <span className="stat-label">Comics Translated</span>
              </div>
              <div className="footer-stat">
                <span className="stat-number">50K+</span>
                <span className="stat-label">Happy Readers</span>
              </div>
              <div className="footer-stat">
                <span className="stat-number">12+</span>
                <span className="stat-label">Languages</span>
              </div>
            </motion.div>
          </div>

          {/* Footer Bottom */}
          <div className="footer-bottom">
            <p>&copy; 2024 Comic Translation Revolution. Breaking barriers, connecting worlds.</p>
          </div>
        </div>
      </footer>
    </>
  );
} 