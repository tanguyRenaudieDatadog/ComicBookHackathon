'use client';

import { motion } from 'framer-motion';
import { Languages, Sparkles, Zap, Globe, Heart, Palette, DollarSign, Bot, Clock, Target, Gift, Gauge } from 'lucide-react';

export function Features() {
const features = [
  {
      icon: <Languages className="feature-icon" />,
      title: "12+ Languages",
      description: "Translate between any supported language with perfect accuracy",
      image: "comicbook.png"
    },
    {
      icon: <Sparkles className="feature-icon" />,
      title: "Context Aware",
      description: "AI understands character names, emotions, and story context",
      image: "translated_comic_c08931ab-736f-498c-881a-5dd28023534b.png"
  },
  {
      icon: <Zap className="feature-icon" />,
      title: "Latest AI Model",
      description: "Powered by cutting-edge technology for superior translations",
      image: "comicbook2.webp"
    },
    {
      icon: <Globe className="feature-icon" />,
      title: "Global Access",
      description: "Making comics and manga accessible to readers worldwide",
      image: "translated_comic_d81f67a6-029d-4cdc-a6eb-9d525c44a0d9.png"
    }
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

  const solutionItems = [
    {
      icon: <Gift className="solution-icon" />,
      title: "Free",
      subtitle: "for everyone",
      comicImage: "comicbook.webp",
      color: "from-green-400 to-green-600"
  },
  {
      icon: <Target className="solution-icon" />,
      title: "Context-aware",
      subtitle: "translations",
      comicImage: "comicbook2.webp",
      color: "from-blue-400 to-blue-600"
    },
    {
      icon: <Gauge className="solution-icon" />,
      title: "Instant",
      subtitle: "results",
      comicImage: "comicbook3.jpg",
      color: "from-purple-400 to-purple-600"
    },
    {
      icon: <Globe className="solution-icon" />,
      title: "12+ languages",
      subtitle: "supported",
      comicImage: "translated_comic_c08931ab-736f-498c-881a-5dd28023534b.png",
      color: "from-orange-400 to-orange-600"
    }
  ];

  return (
    <>
      {/* Problem & Solution Section */}
      <section id="mission" className="problem-section">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="problem-content"
          >
            <h2 className="section-title problem-title">
              <Heart className="title-icon" />
              Breaking Translation Barriers
            </h2>
            <p className="problem-intro">
              Millions of comic and manga fans worldwide face the same frustrating barriers when trying to enjoy stories in their native language.
            </p>
            
            <div className="problems-grid">
              <motion.div 
                className="problem-card expensive"
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
                whileHover={{ scale: 1.02, y: -5 }}
              >
                <div className="problem-icon-wrapper">
                  <DollarSign className="problem-icon-svg" />
                </div>
                <h3>Expensive Costs</h3>
                <p>Professional translation services cost <strong>$500-2000+</strong> per comic issue, making it impossible for most creators and fans to access quality translations.</p>
                <div className="problem-impact">
                  <span className="impact-stat">95% of creators</span>
                  <span className="impact-text">can't afford professional translation</span>
                </div>
              </motion.div>
              
              <motion.div 
                className="problem-card quality"
                initial={{ opacity: 0, x: 0 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                whileHover={{ scale: 1.02, y: -5 }}
              >
                <div className="problem-icon-wrapper">
                  <Bot className="problem-icon-svg" />
                </div>
                <h3>Poor Quality</h3>
                <p>Automated tools produce <strong>broken translations</strong> that lose cultural context, character personalities, and story meaning - ruining the reading experience.</p>
                <div className="problem-impact">
                  <span className="impact-stat">78% of fans</span>
                  <span className="impact-text">abandon poorly translated comics</span>
                </div>
              </motion.div>
              
              <motion.div 
                className="problem-card time"
                initial={{ opacity: 0, x: 50 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                whileHover={{ scale: 1.02, y: -5 }}
              >
                <div className="problem-icon-wrapper">
                  <Clock className="problem-icon-svg" />
                </div>
                <h3>Endless Waiting</h3>
                <p>Human translators take <strong>weeks or months</strong> to complete a single issue, leaving fans waiting indefinitely for their favorite stories to be accessible.</p>
                <div className="problem-impact">
                  <span className="impact-stat">6-12 weeks</span>
                  <span className="impact-text">average wait time per issue</span>
                </div>
              </motion.div>
            </div>

            <motion.div 
              className="solution-banner-visual"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
            >
              <div className="solution-header">
                <h3>Our Solution Changes Everything</h3>
                <p className="solution-description">Experience the future of comic translation with our revolutionary AI technology</p>
              </div>
              
              <div className="solution-visual-grid">
                {solutionItems.map((item, index) => (
                  <motion.div
                    key={item.title}
                    className="solution-item-visual"
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.6, delay: 0.1 * index }}
                    whileHover={{ scale: 1.05, y: -10 }}
                  >
                    <div className="solution-comic-circle">
                      <img src={`/${item.comicImage}`} alt={item.title} />
                      <div className={`solution-gradient-overlay bg-gradient-to-br ${item.color}`}></div>
                    </div>
                    <div className="solution-icon-badge">
                      {item.icon}
                    </div>
                    <div className="solution-text">
                      <span className="solution-title">{item.title}</span>
                      <span className="solution-subtitle">{item.subtitle}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Languages Section */}
      <section id="languages" className="languages">
        <div className="container">
          <h2 className="section-title languages-title">
            <Languages className="title-icon" />
            Supported Languages
          </h2>
          <p className="section-subtitle languages-subtitle">
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

      {/* Features Section - Single Row */}
      <section id="features" className="features">
        <div className="container">
          <h2 className="section-title">
            <Zap className="title-icon" />
            Why Choose Us?
          </h2>
          
          <div className="features-grid-single-row">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="feature-card manga-style"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
                  rotateY: 5,
                }}
              >
                <div className="feature-comic-bg">
                  <img src={`/${feature.image}`} alt={feature.title} />
                  <div className="comic-overlay"></div>
                </div>
                <div className="feature-content">
                  <div className="feature-icon-wrapper">
                    {feature.icon}
                  </div>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </div>
                <div className="feature-glow"></div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
} 