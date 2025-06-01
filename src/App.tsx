import React from 'react';
import { motion } from 'framer-motion';
import { 
  Globe, 
  Languages, 
  Sparkles, 
  Zap, 
  Heart, 
  BookOpen, 
  ArrowRight,
  Star,
  Palette,
  Users
} from 'lucide-react';
import './App.css';

function App() {
  const comicImages = [
    'comicbook.webp',
    'comicbook2.webp', 
    'comicbook3.jpg',
    'translated_comic_c08931ab-736f-498c-881a-5dd28023534b.png',
    'translated_comic_d81f67a6-029d-4cdc-a6eb-9d525c44a0d9.png'
  ];

  const languages = [
    { flag: '🇺🇸', name: 'English' },
    { flag: '🇪🇸', name: 'Spanish' },
    { flag: '🇫🇷', name: 'French' },
    { flag: '🇯🇵', name: 'Japanese' },
    { flag: '🇰🇷', name: 'Korean' },
    { flag: '🇨🇳', name: 'Chinese' },
    { flag: '🇩🇪', name: 'German' },
    { flag: '🇮🇹', name: 'Italian' },
    { flag: '🇷🇺', name: 'Russian' },
    { flag: '🇸🇦', name: 'Arabic' },
    { flag: '🇮🇳', name: 'Hindi' },
    { flag: '🇵🇹', name: 'Portuguese' }
  ];

  const features = [
    {
      icon: <Languages className="feature-icon" />,
      title: "12+ Languages",
      description: "Translate between any of our supported languages with perfect accuracy"
    },
    {
      icon: <Sparkles className="feature-icon" />,
      title: "Context Aware",
      description: "Our AI understands character names, emotions, and story context"
    },
    {
      icon: <Zap className="feature-icon" />,
      title: "Latest Llama Model",
      description: "Powered by cutting-edge AI technology for superior translations"
    },
    {
      icon: <Globe className="feature-icon" />,
      title: "Global Accessibility",
      description: "Making comics and manga accessible to readers worldwide"
    }
  ];

  return (
    <div className="App">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-background">
          {comicImages.map((image, index) => (
            <motion.div
              key={index}
              className="floating-comic"
              style={{ '--delay': `${index * 0.5}s` } as React.CSSProperties}
              animate={{
                y: [0, -20, 0],
                rotate: [0, 5, 0, -5, 0],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                delay: index * 0.5,
              }}
            >
              <img src={`/${image}`} alt="Comic" />
            </motion.div>
          ))}
        </div>
        
        <div className="hero-content">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="hero-text"
          >
            <h1 className="hero-title">
              <span className="gradient-text">Comic</span> & 
              <span className="gradient-text manga">Manga</span><br />
              <span className="hero-subtitle">Translation Revolution</span>
            </h1>
            
            <p className="hero-description">
              🚀 Breaking language barriers in the world of comics and manga! 
              Our AI-powered platform translates your favorite stories with 
              <span className="highlight"> context awareness</span> and 
              <span className="highlight"> cultural sensitivity</span>.
            </p>
            
            <div className="hero-stats">
              <div className="stat">
                <BookOpen className="stat-icon" />
                <span>1000+ Comics Translated</span>
              </div>
              <div className="stat">
                <Users className="stat-icon" />
                <span>50,000+ Happy Readers</span>
              </div>
              <div className="stat">
                <Star className="stat-icon" />
                <span>99.9% Accuracy</span>
              </div>
            </div>
            
            <motion.button
              className="cta-button"
              whileHover={{ scale: 1.05, boxShadow: "0 10px 30px rgba(255,107,107,0.4)" }}
              whileTap={{ scale: 0.95 }}
            >
              Start Translating <ArrowRight className="button-icon" />
            </motion.button>
          </motion.div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="mission">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mission-content"
          >
            <h2 className="section-title">
              <Heart className="title-icon" />
              Our Mission
            </h2>
            <p className="mission-text">
              We believe that <span className="highlight">amazing stories</span> should be accessible to 
              <span className="highlight"> everyone, everywhere</span>. Our mission is to break down language 
              barriers and connect comic and manga lovers across the globe. With our advanced AI technology, 
              we preserve the <span className="highlight">cultural nuances</span>, 
              <span className="highlight"> character personalities</span>, and 
              <span className="highlight"> artistic integrity</span> of every story we translate.
            </p>
            
            <div className="mission-highlights">
              <div className="highlight-box">
                <Palette className="highlight-icon" />
                <h4>Preserving Art</h4>
                <p>Maintaining the original visual storytelling while adapting text seamlessly</p>
              </div>
              <div className="highlight-box">
                <Globe className="highlight-icon" />
                <h4>Global Community</h4>
                <p>Connecting readers worldwide through shared love for comics and manga</p>
              </div>
              <div className="highlight-box">
                <Sparkles className="highlight-icon" />
                <h4>Cultural Bridge</h4>
                <p>Respecting cultural contexts while making stories universally enjoyable</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Languages Section */}
      <section className="languages">
        <div className="container">
          <h2 className="section-title">
            <Languages className="title-icon" />
            Supported Languages
          </h2>
          <p className="section-subtitle">
            Translate between any of these languages with our AI-powered system
          </p>
          
          <div className="languages-grid">
            {languages.map((language, index) => (
              <motion.div
                key={language.name}
                className="language-card"
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ scale: 1.1, rotate: 5 }}
              >
                <span className="language-flag">{language.flag}</span>
                <span className="language-name">{language.name}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <h2 className="section-title">
            <Zap className="title-icon" />
            Why Choose Us?
          </h2>
          
          <div className="features-grid">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="feature-card"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: "0 20px 40px rgba(0,0,0,0.1)"
                }}
              >
                <div className="feature-icon-wrapper">
                  {feature.icon}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Comic Showcase */}
      <section className="showcase">
        <div className="container">
          <h2 className="section-title">
            <BookOpen className="title-icon" />
            See the Magic in Action
          </h2>
          
          <div className="comics-showcase">
            {comicImages.slice(0, 3).map((image, index) => (
              <motion.div
                key={index}
                className="showcase-card"
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                whileHover={{ scale: 1.02 }}
              >
                <img src={`/${image}`} alt={`Comic ${index + 1}`} />
                <div className="showcase-overlay">
                  <h4>Professional Translation</h4>
                  <p>Context-aware • Character consistent • Culturally sensitive</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            className="footer-content"
          >
            <h3>Ready to Explore Stories in Any Language?</h3>
            <p>Join thousands of readers discovering amazing comics and manga from around the world!</p>
            <motion.button
              className="cta-button secondary"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Get Started Now <Sparkles className="button-icon" />
            </motion.button>
          </motion.div>
        </div>
      </footer>
    </div>
  );
}

export default App; 