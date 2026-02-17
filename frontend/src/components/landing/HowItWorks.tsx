'use client';

import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { goToDemo } from '@/lib/navigation';

export function HowItWorks() {
  return (
    <>
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
                onClick={goToDemo}
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