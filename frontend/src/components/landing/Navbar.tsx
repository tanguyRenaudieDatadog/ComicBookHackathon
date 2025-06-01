'use client';

import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import Link from "next/link";
import { Sparkles, Zap, Languages } from "lucide-react";

export function Navbar() {
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <motion.header
      className="navbar-gradient"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <nav className="navbar-container" aria-label="Global">
        {/* Logo Section */}
        <div className="navbar-logo">
          <Link href="/" className="logo-link">
            <motion.div 
              className="logo-content"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Sparkles className="logo-icon" />
              <span className="logo-text">ComicTranslator</span>
            </motion.div>
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <div className="mobile-menu-button">
          <Button variant="ghost" size="icon">
            <span className="sr-only">Open main menu</span>
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            </svg>
          </Button>
        </div>

        {/* Navigation Links */}
        <div className="navbar-links">
          <motion.button 
            onClick={() => scrollToSection('mission')}
            className="nav-link"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Languages className="nav-icon" />
            Mission
          </motion.button>
          <motion.button 
            onClick={() => scrollToSection('languages')}
            className="nav-link"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Sparkles className="nav-icon" />
            Languages
          </motion.button>
          <motion.button 
            onClick={() => scrollToSection('features')}
            className="nav-link"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Zap className="nav-icon" />
            Features
          </motion.button>
          <motion.button 
            onClick={() => scrollToSection('showcase')}
            className="nav-link"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Sparkles className="nav-icon" />
            Examples
          </motion.button>
        </div>

        {/* CTA Button */}
        <div className="navbar-cta">
          <motion.button
            className="navbar-cta-button"
            whileHover={{ 
              scale: 1.05,
              boxShadow: "0 10px 30px rgba(255,107,107,0.4)" 
            }}
            whileTap={{ scale: 0.95 }}
            onClick={() => window.location.href = 'http://localhost:8080'}
          >
            <span>Get Started</span>
            <Zap className="cta-icon" />
          </motion.button>
        </div>
      </nav>
    </motion.header>
  );
} 