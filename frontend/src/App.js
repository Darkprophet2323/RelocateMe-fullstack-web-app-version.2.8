import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import { BrowserRouter as Router, Route, Routes, Link, Navigate, useLocation } from "react-router-dom";
import axios from "axios";
import { gsap } from "gsap";

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Spy Cursor Component - Simple and Reliable Implementation
const SpyCursor = () => {
  const bigBallRef = useRef(null);
  const smallBallRef = useRef(null);

  useEffect(() => {
    const bigBall = bigBallRef.current;
    const smallBall = smallBallRef.current;

    if (!bigBall || !smallBall) return;

    // Add custom cursor class to body
    document.body.classList.add('spy-cursor-active');

    // Simple mouse move handler
    const handleMouseMove = (e) => {
      if (bigBall && smallBall) {
        bigBall.style.left = (e.clientX - 15) + 'px';
        bigBall.style.top = (e.clientY - 15) + 'px';
        smallBall.style.left = (e.clientX - 5) + 'px';
        smallBall.style.top = (e.clientY - 5) + 'px';
      }
    };

    // Simple hover handlers
    const handleMouseEnter = () => {
      if (bigBall) {
        bigBall.style.transform = 'scale(4)';
        bigBall.style.transition = 'transform 0.3s ease';
      }
    };

    const handleMouseLeave = () => {
      if (bigBall) {
        bigBall.style.transform = 'scale(1)';
        bigBall.style.transition = 'transform 0.3s ease';
      }
    };

    // Add event listeners to document
    document.addEventListener('mousemove', handleMouseMove);

    // Function to add hover listeners to all interactive elements
    const addHoverListeners = () => {
      // Remove existing listeners first
      document.querySelectorAll('.hoverable').forEach(element => {
        element.removeEventListener('mouseenter', handleMouseEnter);
        element.removeEventListener('mouseleave', handleMouseLeave);
        element.classList.remove('hoverable');
      });

      // Add to all interactive elements
      const selectors = [
        'button',
        'a',
        'input',
        'textarea',
        'select',
        '[role="button"]',
        '[onclick]',
        'label'
      ];

      selectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(element => {
          element.classList.add('hoverable');
          element.addEventListener('mouseenter', handleMouseEnter);
          element.addEventListener('mouseleave', handleMouseLeave);
        });
      });

      console.log('Added hover listeners to', document.querySelectorAll('.hoverable').length, 'elements');
    };

    // Initial setup
    addHoverListeners();

    // Re-add listeners when DOM changes
    const observer = new MutationObserver(() => {
      setTimeout(addHoverListeners, 100);
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Cleanup
    return () => {
      document.body.classList.remove('spy-cursor-active');
      document.removeEventListener('mousemove', handleMouseMove);
      observer.disconnect();
      
      document.querySelectorAll('.hoverable').forEach(element => {
        element.removeEventListener('mouseenter', handleMouseEnter);
        element.removeEventListener('mouseleave', handleMouseLeave);
      });
    };
  }, []);

  return (
    <div className="cursor">
      <div 
        ref={bigBallRef} 
        className="cursor__ball cursor__ball--big"
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '30px',
          height: '30px',
          pointerEvents: 'none',
          zIndex: 10000,
          mixBlendMode: 'difference'
        }}
      >
        <svg height="30" width="30" style={{ display: 'block' }}>
          <circle cx="15" cy="15" r="12" strokeWidth="0" fill="#f7f8fa"></circle>
        </svg>
      </div>
      
      <div 
        ref={smallBallRef} 
        className="cursor__ball cursor__ball--small"
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '10px',
          height: '10px',
          pointerEvents: 'none',
          zIndex: 10000,
          mixBlendMode: 'difference'
        }}
      >
        <svg height="10" width="10" style={{ display: 'block' }}>
          <circle cx="5" cy="5" r="4" strokeWidth="0" fill="#f7f8fa"></circle>
        </svg>
      </div>
    </div>
  );
};

// MISSION DEBRIEF Noir Button Component
const MissionDebriefButton = () => {
  const handleClick = () => {
    window.open('about:blank', '_blank');
  };

  return (
    <button
      onClick={handleClick}
      className="mission-debrief-button"
      style={{
        position: 'fixed',
        bottom: '120px',
        right: '30px',
        zIndex: 100,
        backgroundColor: '#e0e0e0',
        color: '#000',
        border: 'none',
        padding: '12px 24px',
        fontSize: '14px',
        fontFamily: 'Cinzel, serif',
        fontWeight: 'bold',
        letterSpacing: '1.5px',
        textTransform: 'uppercase',
        cursor: 'pointer',
        borderRadius: '0',
        minHeight: '48px',
        background: `
          linear-gradient(45deg, transparent 49%, rgba(255,255,255,0.1) 50%, transparent 51%),
          linear-gradient(rgba(240,240,240,1) 0%, rgba(200,200,200,1) 100%)
        `,
        backgroundSize: '20px 20px, 100% 100%',
        transition: 'all 0.3s ease',
        animation: 'fadeInDebrief 1.2s ease-out',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)',
        overflow: 'hidden',
        position: 'relative'
      }}
      onMouseEnter={(e) => {
        e.target.style.transform = 'translateY(-2px)';
        e.target.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.4)';
        e.target.querySelector('.arrow').style.transform = 'translateX(3px)';
        
        // Add sweep effect
        const sweep = e.target.querySelector('.sweep-effect');
        if (sweep) {
          sweep.style.transform = 'translateX(100%)';
        }
      }}
      onMouseLeave={(e) => {
        e.target.style.transform = 'translateY(0)';
        e.target.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.3)';
        e.target.querySelector('.arrow').style.transform = 'translateX(0)';
        
        // Reset sweep effect
        const sweep = e.target.querySelector('.sweep-effect');
        if (sweep) {
          sweep.style.transform = 'translateX(-100%)';
        }
      }}
      onMouseDown={(e) => {
        e.target.style.transform = 'translateY(-1px) scale(0.98)';
      }}
      onMouseUp={(e) => {
        e.target.style.transform = 'translateY(-2px) scale(1)';
      }}
    >
      <div 
        className="sweep-effect"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.4) 50%, transparent 70%)',
          transform: 'translateX(-100%)',
          transition: 'transform 0.6s ease',
          pointerEvents: 'none'
        }}
      />
      <span style={{ position: 'relative', zIndex: 1 }}>
        MISSION DEBRIEF
      </span>
      <span 
        className="arrow"
        style={{
          marginLeft: '8px',
          transition: 'transform 0.3s ease',
          position: 'relative',
          zIndex: 1
        }}
      >
        →
      </span>
      
      <style jsx>{`
        @keyframes fadeInDebrief {
          0% {
            opacity: 0;
            transform: translateY(20px) scale(0.9);
          }
          50% {
            opacity: 0.7;
            transform: translateY(-5px) scale(1.02);
          }
          100% {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
        
        .mission-debrief-button {
          font-family: 'Cinzel', serif !important;
        }
        
        @media (max-width: 768px) {
          .mission-debrief-button {
            fontSize: '12px !important';
            padding: '12px 20px !important';
            letterSpacing: '1px !important';
            bottom: '80px !important';
            right: '20px !important';
          }
        }
        
        @media (max-width: 480px) {
          .mission-debrief-button {
            fontSize: '10px !important';
            padding: '10px 16px !important';
            letterSpacing: '0.8px !important';
            bottom: '60px !important';
            right: '15px !important';
          }
        }
      `}</style>
    </button>
  );
};

// Enhanced Progress Wizard Component with Noir Theme
const ProgressWizard = ({ currentStep, totalSteps, completedSteps }) => {
  const progressPercentage = (completedSteps / totalSteps) * 100;
  
  return (
    <div className="mb-8 bg-black border border-gray-600 shadow-lg p-8 fade-in">
      <h2 className="text-3xl font-bold text-white mb-6 noir-title">PROGRESS TRACKING</h2>
      <div className="flex items-center justify-between mb-6">
        <span className="text-sm font-mono text-gray-300 uppercase tracking-wider">STEP {currentStep} OF {totalSteps}</span>
        <span className="text-sm font-mono text-gray-300 uppercase tracking-wider">{Math.round(progressPercentage)}% COMPLETE</span>
      </div>
      <div className="w-full bg-gray-800 h-2 mb-6 border border-gray-600">
        <div 
          className="bg-white h-full transition-all duration-1000 ease-out relative"
          style={{ width: `${progressPercentage}%` }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-50 animate-pulse"></div>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-700 p-4 text-center">
          <div className="text-3xl font-bold text-white font-mono">{completedSteps}</div>
          <div className="text-sm text-gray-400 uppercase tracking-wider">COMPLETED</div>
        </div>
        <div className="bg-gray-900 border border-gray-700 p-4 text-center">
          <div className="text-3xl font-bold text-white font-mono">{totalSteps - completedSteps}</div>
          <div className="text-sm text-gray-400 uppercase tracking-wider">REMAINING</div>
        </div>
        <div className="bg-gray-900 border border-gray-700 p-4 text-center">
          <div className="text-3xl font-bold text-white font-mono">{totalSteps}</div>
          <div className="text-sm text-gray-400 uppercase tracking-wider">TOTAL</div>
        </div>
      </div>
    </div>
  );
};

// Navigation Component - Compact Header with Space for Logout
const Navigation = ({ user, onLogout, currentPath }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  const navItems = [
    { path: "/dashboard", name: "DASHBOARD", step: 1, description: "MISSION CONTROL" },
    { path: "/timeline", name: "TIMELINE", step: 2, description: "OPERATIONAL SCHEDULE" },
    { path: "/progress", name: "PROGRESS", step: 3, description: "STATUS TRACKING" },
    { path: "/visa", name: "LEGAL", step: 4, description: "DOCUMENTATION" },
    { path: "/employment", name: "WORK", step: 5, description: "CAREER SEARCH" },
    { path: "/housing", name: "HOUSING", step: 6, description: "LOCATION INTEL" },
    { path: "/logistics", name: "LOGISTICS", step: 7, description: "MOVEMENT OPS" },
    { path: "/analytics", name: "ANALYTICS", step: 8, description: "DATA ANALYSIS" },
    { path: "/resources", name: "RESOURCES", step: 9, description: "SUPPORT NETWORK" }
  ];

  return (
    <nav className="bg-black bg-opacity-95 backdrop-blur-sm border-b border-gray-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6">
        <div className="flex justify-between h-14">
          
          {/* Desktop Navigation - Full Width */}
          <div className="hidden md:flex items-center space-x-1 flex-1">
            {navItems.map(item => (
              <Link
                key={item.path}
                to={item.path}
                className={`hoverable px-3 py-2 text-xs font-mono font-semibold tracking-wider transition-all duration-300 relative group border-b-2 ${
                  currentPath === item.path
                    ? 'text-white border-white bg-gray-900'
                    : 'text-gray-400 hover:text-white border-transparent hover:border-gray-500 hover:bg-gray-900'
                }`}
              >
                <span className="mr-1 text-gray-600">[{item.step}]</span>
                {item.name}
                
                {/* Enhanced Tooltip */}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 px-3 py-2 bg-black border border-gray-600 text-white text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-50 font-mono rounded-md">
                  {item.description}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-b-black"></div>
                </div>
              </Link>
            ))}
          </div>

          {/* Desktop User Controls */}
          <div className="hidden md:flex items-center space-x-3">
            <span className="text-gray-300 text-xs font-mono">USER: {user.toUpperCase()}</span>
            <button
              onClick={onLogout}
              className="hoverable logout-button"
            >
              [LOGOUT]
            </button>
          </div>

          {/* Mobile Header */}
          <div className="md:hidden flex items-center justify-between w-full">
            <span className="text-white text-sm font-mono font-bold">RELOCATE.SYS</span>
            <div className="flex items-center space-x-2">
              <span className="text-gray-300 text-xs font-mono">USER: {user.toUpperCase()}</span>
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="hoverable text-gray-400 hover:text-white p-2 rounded-md transition-colors duration-300"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {isMobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        {/* Enhanced Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden pb-3 animate-slideDown">
            <div className="grid grid-cols-2 gap-2 mb-3">
              {navItems.map(item => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`hoverable text-center py-3 px-2 text-xs font-mono border rounded-md transition-all duration-300 ${
                    currentPath === item.path
                      ? 'bg-white text-black border-white'
                      : 'bg-gray-900 text-gray-300 border-gray-600 hover:bg-gray-800 hover:border-gray-400 hover:text-white'
                  }`}
                >
                  <div className="font-semibold">[{item.step}] {item.name}</div>
                  <div className="text-xs opacity-75 mt-1">{item.description}</div>
                </Link>
              ))}
            </div>
            <div className="flex justify-center">
              <button
                onClick={onLogout}
                className="hoverable logout-button"
              >
                [LOGOUT]
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

// Enhanced Dashboard with Noir Theme
const DashboardPage = () => {
  const [stats, setStats] = useState({
    total_steps: 34,
    completed_steps: 0,
    in_progress: 0,
    urgent_tasks: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/api/dashboard/overview`);
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      }
    };
    fetchStats();
  }, []);

  const quickStartSteps = [
    {
      title: "DOCUMENTATION PHASE",
      description: "Gather critical documents: passport, certificates, financial records.",
      action: "ACCESS LEGAL SECTION",
      link: "/visa",
      urgent: true,
      icon: "📋"
    },
    {
      title: "TIMELINE ANALYSIS",
      description: "Review 34-step operational timeline for relocation protocol.",
      action: "VIEW TIMELINE",
      link: "/timeline",
      urgent: false,
      icon: "📅"
    },
    {
      title: "EMPLOYMENT SEARCH",
      description: "Scout 8 verified opportunities in target region.",
      action: "BROWSE POSITIONS",
      link: "/employment",
      urgent: false,
      icon: "💼"
    }
  ];

  const essentialLinks = [
    { name: "UK GOVERNMENT", url: "https://www.gov.uk", description: "Official state portal" },
    { name: "VISA CENTRAL", url: "https://www.gov.uk/browse/visas-immigration", description: "Immigration command" },
    { name: "PEAK DISTRICT HQ", url: "https://www.peakdistrict.gov.uk", description: "Target region intel" },
    { name: "NHS REGISTRATION", url: "https://www.nhs.uk/using-the-nhs/nhs-services/gps/how-to-register-with-a-gp-practice/", description: "Medical system access" },
    { 
      name: "Mission Debrief: Mission Console", 
      url: "https://os-theme-verify.emergent.host/", 
      description: "OS Noir Command Interface", 
      special: true 
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12 fade-in">
          <h1 className="text-6xl md:text-8xl font-bold font-serif text-white mb-6 typewriter">
            RELOCATION
          </h1>
          <div className="text-2xl md:text-4xl font-mono text-gray-300 mb-8 tracking-widest">
            [ MISSION: PHOENIX → PEAK DISTRICT ]
          </div>
          <p className="text-lg text-gray-400 mb-8 max-w-3xl mx-auto font-mono leading-relaxed">
            CLASSIFIED OPERATION: International relocation protocol from Phoenix, Arizona to Peak District, UK. 
            Follow systematic approach for mission success.
          </p>
          
          {/* Progress Overview */}
          <ProgressWizard 
            currentStep={stats.completed_steps + 1} 
            totalSteps={stats.total_steps} 
            completedSteps={stats.completed_steps} 
          />
        </div>

        {/* Quick Start Mission Briefing */}
        <div className="mb-12 slide-in-left">
          <h2 className="text-3xl font-bold text-white mb-8 font-serif text-center">MISSION BRIEFING</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quickStartSteps.map((step, index) => (
              <div key={index} className={`bg-black border-2 p-8 transition-all duration-500 hover:border-white hover:bg-gray-900 group ${step.urgent ? 'border-red-600' : 'border-gray-600'}`}>
                {step.urgent && (
                  <div className="flex items-center mb-4">
                    <span className="bg-red-900 text-red-200 text-xs font-mono font-bold px-3 py-1 border border-red-700 tracking-wider">
                      PRIORITY ALPHA
                    </span>
                  </div>
                )}
                <div className="text-4xl mb-4">{step.icon}</div>
                <h3 className="text-xl font-bold text-white mb-4 font-mono tracking-wide">{step.title}</h3>
                <p className="text-gray-400 mb-6 leading-relaxed">{step.description}</p>
                <Link 
                  to={step.link}
                  className="inline-block bg-white text-black px-6 py-3 font-mono font-bold text-sm tracking-wider hover:bg-gray-200 transition-all duration-300 border-2 border-white group-hover:bg-black group-hover:text-white"
                >
                  {step.action} →
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* Status Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-black border border-gray-600 p-6 text-center hover:border-white transition-all duration-300">
            <div className="text-4xl font-bold text-white mb-2 font-mono">{stats.total_steps}</div>
            <div className="text-gray-400 text-sm font-mono tracking-wider">TOTAL OBJECTIVES</div>
          </div>
          <div className="bg-black border border-gray-600 p-6 text-center hover:border-white transition-all duration-300">
            <div className="text-4xl font-bold text-white mb-2 font-mono">{stats.completed_steps}</div>
            <div className="text-gray-400 text-sm font-mono tracking-wider">OBJECTIVES COMPLETE</div>
          </div>
          <div className="bg-black border border-gray-600 p-6 text-center hover:border-white transition-all duration-300">
            <div className="text-4xl font-bold text-white mb-2 font-mono">{stats.in_progress}</div>
            <div className="text-gray-400 text-sm font-mono tracking-wider">IN PROGRESS</div>
          </div>
          <div className="bg-black border border-gray-600 p-6 text-center hover:border-white transition-all duration-300">
            <div className="text-4xl font-bold text-white mb-2 font-mono">{stats.urgent_tasks}</div>
            <div className="text-gray-400 text-sm font-mono tracking-wider">CRITICAL TASKS</div>
          </div>
        </div>

        {/* Essential Command Links */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-white mb-8 font-serif text-center">ESSENTIAL COMMAND LINKS</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {essentialLinks.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => {
                  if (link.special) {
                    e.preventDefault();
                    window.open(link.url, '_blank', 'noopener,noreferrer');
                  }
                }}
                className={`hoverable bg-black border border-gray-600 p-6 hover:border-white hover:bg-gray-900 transition-all duration-300 group block ${
                  link.special ? 'bg-red-900 border-red-700 hover:bg-red-800 text-black' : ''
                }`}
              >
                <h3 className={`font-bold mb-3 font-mono tracking-wide group-hover:text-gray-200 ${
                  link.special ? 'text-black' : 'text-white'
                }`}>{link.name}</h3>
                <p className={`text-sm font-mono ${
                  link.special ? 'text-black opacity-80' : 'text-gray-400'
                }`}>{link.description}</p>
              </a>
            ))}
          </div>
        </div>

        {/* Mission Control Center */}
        <div className="bg-black border border-gray-600 p-8 text-center hover:border-white transition-all duration-300">
          <h2 className="text-3xl font-bold text-white mb-6 font-serif">MISSION CONTROL</h2>
          <p className="text-gray-400 mb-8 font-mono text-lg leading-relaxed">
            Ready to commence relocation protocol. Select operational mode to begin systematic progression 
            toward target destination. All systems operational.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/timeline"
              className="bg-white text-black px-8 py-4 font-mono font-bold tracking-wider hover:bg-gray-200 transition-all duration-300 border-2 border-white"
            >
              [TIMELINE] INITIATE SEQUENCE
            </Link>
            <Link 
              to="/progress"
              className="bg-transparent text-white px-8 py-4 font-mono font-bold tracking-wider border-2 border-white hover:bg-white hover:text-black transition-all duration-300"
            >
              [PROGRESS] STATUS CHECK
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

// Enhanced Timeline Page with Noir Theme
const TimelinePage = () => {
  const [timelineData, setTimelineData] = useState({
    timeline: [],
    categories: {}
  });
  const [activeCategory, setActiveCategory] = useState('all');
  const [completedCount, setCompletedCount] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${API}/api/timeline/full`);
        setTimelineData({
          timeline: response.data.timeline || [],
          categories: {}
        });
        
        // Count completed steps
        const completed = (response.data.timeline || []).filter(step => step.is_completed).length;
        setCompletedCount(completed);
      } catch (error) {
        console.error('Error fetching timeline data:', error);
        // Use fallback data
        setTimelineData({
          timeline: [
            { id: 1, title: "Initial Research & Decision", description: "Research Peak District areas, cost of living, and lifestyle", category: "Planning", is_completed: false },
            { id: 2, title: "Create Relocation Budget", description: "Calculate moving costs, visa fees, initial living expenses", category: "Planning", is_completed: false },
            { id: 3, title: "Visa Research", description: "Determine visa type needed (work, skilled worker, family, etc.)", category: "Visa & Legal", is_completed: false }
          ],
          categories: {}
        });
      }
    };
    fetchData();
  }, []);

  const updateStepProgress = async (stepId, completed) => {
    try {
      await axios.post(`${API}/api/timeline/update-progress`, {
        step_id: stepId,
        completed: completed
      });
      
      // Refresh timeline data
      const response = await axios.get(`${API}/api/timeline/full`);
      setTimelineData({
        timeline: response.data.timeline || [],
        categories: {}
      });
      
      // Update completed count
      const newCompleted = (response.data.timeline || []).filter(step => step.is_completed).length;
      setCompletedCount(newCompleted);
      
    } catch (error) {
      console.error('Error updating step progress:', error);
    }
  };

  const filteredSteps = timelineData.timeline || [];

  const timelineLinks = [
    { name: "UK GOV TIMELINE", url: "https://www.gov.uk/browse/visas-immigration", description: "Official protocol guidance" },
    { name: "MOVE CALCULATOR", url: "https://www.internationalmovers.com/international-moving-timeline", description: "Logistics timeline tool" },
    { name: "EXPAT PROTOCOLS", url: "https://www.expatfocus.com/expatriate-relocation-checklist", description: "Standard operating procedures" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 fade-in">
          <h1 className="text-5xl font-bold font-serif text-white mb-6">
            OPERATIONAL TIMELINE
          </h1>
          <p className="text-xl text-gray-400 mb-8 font-mono tracking-wide">
            [ 34-STEP RELOCATION PROTOCOL: PHOENIX → PEAK DISTRICT ]
          </p>
          
          <ProgressWizard 
            currentStep={completedCount + 1} 
            totalSteps={filteredSteps.length} 
            completedSteps={completedCount} 
          />
        </div>

        {/* Timeline Resources */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 font-mono text-center tracking-wider">REFERENCE MATERIALS</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {timelineLinks.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-black border border-gray-600 p-6 hover:border-white hover:bg-gray-900 transition-all duration-300"
              >
                <h3 className="font-bold text-white mb-3 font-mono tracking-wide">{link.name}</h3>
                <p className="text-gray-400 text-sm font-mono">{link.description}</p>
              </a>
            ))}
          </div>
        </div>

        {/* Timeline Steps */}
        <div className="space-y-6">
          {filteredSteps.map((step, index) => (
            <div
              key={step.id}
              className={`bg-black border-2 p-8 transition-all duration-500 hover:bg-gray-900 ${
                step.is_completed ? 'border-white bg-gray-900' : 'border-gray-600 hover:border-gray-400'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-6">
                    <div className="mr-6 flex-shrink-0">
                      <div className={`w-12 h-12 border-2 flex items-center justify-center font-bold text-lg font-mono ${
                        step.is_completed ? 'bg-white text-black border-white' : 'bg-black text-white border-gray-600'
                      }`}>
                        {step.is_completed ? '✓' : String(index + 1).padStart(2, '0')}
                      </div>
                    </div>
                    <div className="flex-1">
                      <label className="flex items-center cursor-pointer group">
                        <input
                          type="checkbox"
                          checked={step.is_completed}
                          onChange={(e) => updateStepProgress(step.id, e.target.checked)}
                          className="mr-4 w-6 h-6 border-2 border-gray-600 bg-black checked:bg-white checked:border-white appearance-none cursor-pointer relative"
                          style={{
                            backgroundImage: step.is_completed ? "url(\"data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='black' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-7.5 7.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6 10.293l7.146-7.147a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e\")" : 'none'
                          }}
                        />
                        <h3 className={`text-2xl font-bold font-mono tracking-wide transition-all duration-300 ${
                          step.is_completed ? 'text-white line-through' : 'text-white group-hover:text-gray-300'
                        }`}>
                          {step.title}
                        </h3>
                      </label>
                      <div className="flex items-center mt-3 space-x-4">
                        <span className="px-3 py-1 text-sm border border-gray-600 text-gray-300 font-mono tracking-wider uppercase">
                          {step.category}
                        </span>
                      </div>
                    </div>
                  </div>
                  <p className="text-gray-300 mb-6 leading-relaxed font-mono">{step.description}</p>
                </div>
                
                {step.is_completed && (
                  <div className="ml-6 text-white text-3xl">
                    ✅
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {filteredSteps.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg font-mono">LOADING OPERATIONAL DATA...</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Enhanced Progress Page with Interactive Checklist and Noir Theme
const ProgressPage = () => {
  const [progressItems, setProgressItems] = useState([]);
  const [editingNotes, setEditingNotes] = useState(null);
  const [tempNote, setTempNote] = useState('');

  useEffect(() => {
    fetchProgressItems();
  }, []);

  const fetchProgressItems = async () => {
    try {
      const response = await axios.get(`${API}/api/progress/items`);
      setProgressItems(response.data.items || []);
    } catch (error) {
      console.error('Error fetching progress items:', error);
      // Use fallback data
      setProgressItems([
        {
          id: '1',
          title: 'Gather Birth Certificate',
          description: 'Obtain certified copy of birth certificate for visa application',
          status: 'completed',
          category: 'Documentation',
          subtasks: [
            { task: 'Request birth certificate online', completed: true },
            { task: 'Pay processing fee', completed: true },
            { task: 'Receive by mail', completed: true }
          ],
          notes: 'Received certified copy from state office. Cost $25.'
        },
        {
          id: '2',
          title: 'Complete Visa Application Form',
          description: 'Fill out UK Skilled Worker visa application online',
          status: 'in_progress',
          category: 'Visa Application',
          subtasks: [
            { task: 'Create UK government account', completed: true },
            { task: 'Fill application form', completed: false },
            { task: 'Upload documents', completed: false }
          ],
          notes: 'Application 70% complete.'
        }
      ]);
    }
  };

  const updateItemStatus = async (itemId, newStatus) => {
    try {
      await axios.put(`${API}/api/progress/items/${itemId}`, {
        status: newStatus
      });
      fetchProgressItems();
    } catch (error) {
      console.error('Error updating item status:', error);
    }
  };

  const toggleSubtask = async (itemId, subtaskIndex) => {
    try {
      await axios.post(`${API}/api/progress/items/${itemId}/subtasks/${subtaskIndex}/toggle`);
      fetchProgressItems();
    } catch (error) {
      console.error('Error toggling subtask:', error);
    }
  };

  const saveNotes = async (itemId, notes) => {
    try {
      await axios.put(`${API}/api/progress/items/${itemId}`, {
        notes: notes
      });
      setEditingNotes(null);
      setTempNote('');
      fetchProgressItems();
    } catch (error) {
      console.error('Error saving notes:', error);
    }
  };

  const startEditingNotes = (item) => {
    setEditingNotes(item.id);
    setTempNote(item.notes || '');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'border-white text-white bg-gray-900';
      case 'in_progress': return 'border-yellow-600 text-yellow-400 bg-yellow-900';
      case 'blocked': return 'border-red-600 text-red-400 bg-red-900';
      default: return 'border-gray-600 text-gray-300 bg-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'in_progress': return '🔄';
      case 'blocked': return '🚫';
      default: return '⏳';
    }
  };

  const completedItems = progressItems.filter(item => item.status === 'completed').length;
  const totalItems = progressItems.length;

  const progressLinks = [
    { name: "TRELLO COMMAND", url: "https://trello.com", description: "Task management system" },
    { name: "MOVING INTEL", url: "https://www.moving.com/tips/moving-checklist/", description: "Operational guidelines" },
    { name: "MOBILE APPS", url: "https://www.apartmenttherapy.com/best-moving-apps-36683126", description: "Field support tools" },
    { name: "EXPAT NETWORK", url: "https://www.internations.org", description: "Agent network access" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 fade-in">
          <h1 className="text-5xl font-bold font-serif text-white mb-6">
            STATUS TRACKING
          </h1>
          <p className="text-xl text-gray-400 mb-8 font-mono tracking-wide">
            [ INTERACTIVE MISSION PROGRESS MONITOR ]
          </p>
          
          <ProgressWizard 
            currentStep={completedItems + 1} 
            totalSteps={totalItems} 
            completedSteps={completedItems} 
          />
        </div>

        {/* Progress Resources */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 font-mono text-center tracking-wider">SUPPORT SYSTEMS</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {progressLinks.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-black border border-gray-600 p-4 hover:border-white hover:bg-gray-900 transition-all duration-300"
              >
                <h3 className="font-bold text-white mb-2 font-mono tracking-wide">{link.name}</h3>
                <p className="text-gray-400 text-sm font-mono">{link.description}</p>
              </a>
            ))}
          </div>
        </div>

        {/* Progress Items */}
        <div className="space-y-6">
          {progressItems.map((item, index) => (
            <div key={item.id} className="bg-black border border-gray-600 p-8 transition-all duration-300 hover:border-white hover:bg-gray-900">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center space-x-6">
                  <div className={`w-16 h-16 border-2 flex items-center justify-center text-2xl font-bold font-mono ${
                    item.status === 'completed' ? 'bg-white text-black border-white' : 
                    item.status === 'in_progress' ? 'bg-yellow-900 border-yellow-600 text-yellow-400' :
                    item.status === 'blocked' ? 'bg-red-900 border-red-600 text-red-400' : 'bg-gray-800 border-gray-600 text-gray-300'
                  }`}>
                    {getStatusIcon(item.status)}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white font-mono tracking-wide">{item.title}</h2>
                    <span className={`inline-block px-4 py-2 text-sm font-mono font-bold tracking-wider uppercase border ${getStatusColor(item.status)}`}>
                      {item.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <select
                    value={item.status}
                    onChange={(e) => updateItemStatus(item.id, e.target.value)}
                    className="border-2 border-gray-600 bg-black text-white px-4 py-2 font-mono focus:border-white focus:outline-none transition-all duration-300"
                  >
                    <option value="not_started">NOT STARTED</option>
                    <option value="in_progress">IN PROGRESS</option>
                    <option value="completed">COMPLETED</option>
                    <option value="blocked">BLOCKED</option>
                  </select>
                </div>
              </div>

              <p className="text-gray-300 mb-6 leading-relaxed font-mono">{item.description}</p>

              {/* Progress Bar */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-3">
                  <span className="text-sm font-mono text-gray-400 tracking-wider uppercase">SUBTASK PROGRESS</span>
                  <span className="text-sm text-gray-400 font-mono">
                    {item.subtasks.filter(st => st.completed).length}/{item.subtasks.length}
                  </span>
                </div>
                <div className="w-full bg-gray-800 h-2 border border-gray-600">
                  <div 
                    className="bg-white h-full transition-all duration-500 relative"
                    style={{ 
                      width: `${(item.subtasks.filter(st => st.completed).length / item.subtasks.length) * 100}%` 
                    }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-50 animate-pulse"></div>
                  </div>
                </div>
              </div>

              {/* Interactive Subtasks */}
              <div className="space-y-4 mb-8">
                <h3 className="font-semibold text-white font-mono tracking-wider">TASK CHECKLIST:</h3>
                {item.subtasks.map((subtask, subIndex) => (
                  <label key={subIndex} className="flex items-center cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={subtask.completed}
                      onChange={() => toggleSubtask(item.id, subIndex)}
                      className="mr-4 w-6 h-6 border-2 border-gray-600 bg-black checked:bg-white checked:border-white appearance-none cursor-pointer relative transition-all duration-200"
                      style={{
                        backgroundImage: subtask.completed ? "url(\"data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='black' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-7.5 7.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6 10.293l7.146-7.147a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e\")" : 'none'
                      }}
                    />
                    <span className={`font-mono transition-all duration-200 group-hover:text-white ${
                      subtask.completed ? 'line-through text-gray-500' : 'text-gray-300'
                    }`}>
                      {subtask.task}
                    </span>
                    {subtask.completed && (
                      <span className="ml-3 text-white">✅</span>
                    )}
                  </label>
                ))}
              </div>

              {/* Notes Section */}
              <div className="border-t border-gray-700 pt-6">
                <h3 className="font-semibold text-white mb-4 font-mono tracking-wider">OPERATIONAL NOTES:</h3>
                {editingNotes === item.id ? (
                  <div className="space-y-4">
                    <textarea
                      value={tempNote}
                      onChange={(e) => setTempNote(e.target.value)}
                      className="w-full p-4 border-2 border-gray-600 bg-black text-white font-mono focus:border-white focus:outline-none transition-all duration-300"
                      rows="4"
                      placeholder="Enter operational notes..."
                    />
                    <div className="flex space-x-4">
                      <button
                        onClick={() => saveNotes(item.id, tempNote)}
                        className="bg-white text-black px-6 py-3 border-2 border-white hover:bg-gray-200 transition-all duration-300 font-mono font-bold tracking-wider"
                      >
                        [SAVE]
                      </button>
                      <button
                        onClick={() => {
                          setEditingNotes(null);
                          setTempNote('');
                        }}
                        className="bg-transparent text-white px-6 py-3 border-2 border-gray-600 hover:border-white transition-all duration-300 font-mono font-bold tracking-wider"
                      >
                        [CANCEL]
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="bg-gray-900 border border-gray-700 p-4">
                      <p className="text-gray-300 font-mono leading-relaxed">
                        {item.notes || 'No operational notes recorded. Click "EDIT NOTES" to add intelligence data.'}
                      </p>
                    </div>
                    <button
                      onClick={() => startEditingNotes(item)}
                      className="text-white hover:text-gray-300 font-mono font-bold tracking-wider"
                    >
                      [EDIT NOTES]
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {progressItems.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-6">📋</div>
            <h2 className="text-3xl font-bold text-white mb-4 font-serif">NO ACTIVE MISSIONS</h2>
            <p className="text-gray-400 font-mono">Initialize timeline sequence to generate progress items.</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Visa & Legal Page with Interactive Document Checklist and Noir Theme
const VisaPage = () => {
  const [visaRequirements, setVisaRequirements] = useState({ visa_types: [] });
  const [selectedVisa, setSelectedVisa] = useState(null);
  const [documentChecklist, setDocumentChecklist] = useState({});

  useEffect(() => {
    const fetchVisaData = async () => {
      try {
        const response = await axios.get(`${API}/api/visa/requirements`);
        setVisaRequirements(response.data);
        if (response.data.visa_types && response.data.visa_types.length > 0) {
          setSelectedVisa(response.data.visa_types[0]);
        }
      } catch (error) {
        console.error('Error fetching visa data:', error);
        // Use fallback data
        const fallbackData = {
          visa_types: [
            {
              id: '1',
              visa_type: 'Skilled Worker Visa',
              fee: '£719 - £1,423',
              processing_time: '3-8 weeks',
              requirements: ['Job offer from UK employer', 'Certificate of sponsorship', 'English language proficiency'],
              application_process: ['Secure job offer', 'Receive certificate', 'Apply online', 'Attend biometric appointment'],
              required_documents: {
                'identity': ['Valid passport', 'Birth certificate', 'Marriage certificate'],
                'financial': ['Bank statements', 'Salary evidence', 'Tax returns'],
                'employment': ['Job offer letter', 'Certificate of sponsorship', 'Qualifications']
              }
            }
          ]
        };
        setVisaRequirements(fallbackData);
        setSelectedVisa(fallbackData.visa_types[0]);
      }
    };
    fetchVisaData();
  }, []);

  const toggleDocument = (category, docIndex) => {
    const key = `${category}_${docIndex}`;
    setDocumentChecklist(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const getDocumentProgress = () => {
    const checkedDocs = Object.values(documentChecklist).filter(Boolean).length;
    const totalDocs = Object.keys(documentChecklist).length;
    return { checked: checkedDocs, total: totalDocs };
  };

  if (!selectedVisa) {
    return <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-xl text-white font-mono">LOADING CLASSIFIED DATA...</div>
    </div>;
  }

  const progress = getDocumentProgress();
  const progressPercentage = progress.total > 0 ? (progress.checked / progress.total) * 100 : 0;

  const visaLinks = [
    { name: "UK GOV PORTAL", url: "https://www.gov.uk/browse/visas-immigration", description: "Official state immigration command" },
    { name: "LEGAL COUNSEL", url: "https://www.lawsociety.org.uk", description: "Qualified immigration attorneys" },
    { name: "DOCUMENT SERVICES", url: "https://www.gov.uk/get-document-legalised", description: "Authorization and apostille" },
    { name: "APPLICATION CENTER", url: "https://www.vfsglobal.co.uk", description: "Biometric processing facilities" },
    { name: "LANGUAGE TESTING", url: "https://www.ielts.org", description: "English proficiency certification" },
    { name: "MEDICAL EXAM", url: "https://www.gov.uk/tb-test-visa", description: "Health screening requirements" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 fade-in">
          <h1 className="text-5xl font-bold font-serif text-white mb-6">
            LEGAL DOCUMENTATION
          </h1>
          <p className="text-xl text-gray-400 mb-8 font-mono tracking-wide">
            [ VISA REQUIREMENTS & CLASSIFICATION PROTOCOLS ]
          </p>
          
          {/* Document Progress */}
          <div className="bg-black border border-gray-600 p-8 mb-8 hover:border-white transition-all duration-300">
            <h2 className="text-3xl font-bold text-white mb-6 font-mono tracking-wider">DOCUMENT STATUS</h2>
            <div className="flex items-center justify-between mb-6">
              <span className="text-sm font-mono text-gray-400 tracking-wider uppercase">DOCUMENTS VERIFIED</span>
              <span className="text-sm font-mono text-gray-400 tracking-wider">{progress.checked} OF {progress.total}</span>
            </div>
            <div className="w-full bg-gray-800 h-3 mb-6 border border-gray-600">
              <div 
                className="bg-white h-full transition-all duration-1000 ease-out relative"
                style={{ width: `${progressPercentage}%` }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-50 animate-pulse"></div>
              </div>
            </div>
            <p className="text-gray-300 font-mono">
              {progress.checked === progress.total && progress.total > 0 
                ? "✅ ALL DOCUMENTS VERIFIED - READY FOR SUBMISSION" 
                : `CONTINUE VERIFICATION: ${progress.total - progress.checked} DOCUMENTS PENDING`
              }
            </p>
          </div>
        </div>

        {/* Visa Resources */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 font-mono text-center tracking-wider">SUPPORT NETWORKS</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {visaLinks.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-black border border-gray-600 p-4 hover:border-white hover:bg-gray-900 transition-all duration-300"
              >
                <h3 className="font-bold text-white mb-2 font-mono tracking-wide">{link.name}</h3>
                <p className="text-gray-400 text-sm font-mono">{link.description}</p>
              </a>
            ))}
          </div>
        </div>

        {/* Selected Visa Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Visa Information */}
          <div className="bg-black border border-gray-600 p-8 hover:border-white transition-all duration-300">
            <h2 className="text-2xl font-bold text-white mb-6 font-mono tracking-wider">
              {selectedVisa.visa_type.toUpperCase()} SPECS
            </h2>
            <div className="space-y-6">
              <div className="flex justify-between items-center p-4 bg-gray-900 border border-gray-700">
                <span className="font-mono text-gray-300">APPLICATION FEE:</span>
                <span className="text-xl font-bold text-white font-mono">{selectedVisa.fee}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gray-900 border border-gray-700">
                <span className="font-mono text-gray-300">PROCESSING TIME:</span>
                <span className="text-xl font-bold text-white font-mono">{selectedVisa.processing_time}</span>
              </div>
              <div className="p-4 bg-gray-900 border border-gray-700">
                <h3 className="font-semibold mb-3 text-white font-mono tracking-wider">REQUIREMENTS:</h3>
                <ul className="space-y-2">
                  {selectedVisa.requirements && selectedVisa.requirements.map((req, index) => (
                    <li key={index} className="text-sm text-gray-300 flex items-start font-mono">
                      <span className="text-white mr-3">▸</span>
                      {req}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Application Process */}
          <div className="bg-black border border-gray-600 p-8 hover:border-white transition-all duration-300">
            <h2 className="text-2xl font-bold text-white mb-6 font-mono tracking-wider">
              OPERATION SEQUENCE
            </h2>
            <div className="space-y-6">
              {selectedVisa.application_process && selectedVisa.application_process.map((step, index) => (
                <div key={index} className="flex items-start">
                  <div className="flex-shrink-0 w-10 h-10 bg-white text-black border-2 border-white flex items-center justify-center font-bold text-sm mr-4 font-mono">
                    {String(index + 1).padStart(2, '0')}
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-300 font-mono">{step}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Interactive Document Checklist */}
        <div className="bg-black border border-gray-600 p-8 hover:border-white transition-all duration-300">
          <h2 className="text-2xl font-bold text-white mb-8 font-mono tracking-wider">
            DOCUMENT VERIFICATION CHECKLIST
          </h2>
          <p className="text-gray-300 mb-8 font-mono leading-relaxed">
            Verify each document as collected. This system tracks progress and ensures compliance with requirements.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {selectedVisa.required_documents && Object.entries(selectedVisa.required_documents).map(([category, documents], categoryIndex) => {
              const colors = [
                'border-l-white bg-gray-900',
                'border-l-gray-400 bg-gray-900',
                'border-l-gray-500 bg-gray-900'
              ];
              
              const categoryDocs = Array.isArray(documents) ? documents.filter(doc => doc.trim() !== '') : [];
              const checkedInCategory = categoryDocs.filter((_, docIndex) => 
                documentChecklist[`${category}_${docIndex}`]
              ).length;
              
              return (
                <div key={category} className={`border-l-4 border border-gray-600 p-6 transition-all duration-300 hover:border-white ${colors[categoryIndex % colors.length]}`}>
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-bold text-white capitalize font-mono tracking-wider">
                      {category.replace('_', ' ')}
                    </h3>
                    <span className="bg-white text-black px-3 py-1 text-sm font-mono font-bold tracking-wider">
                      {checkedInCategory}/{categoryDocs.length}
                    </span>
                  </div>
                  
                  <ul className="space-y-4">
                    {categoryDocs.map((doc, docIndex) => {
                      const isChecked = documentChecklist[`${category}_${docIndex}`];
                      return (
                        <li key={docIndex} className="flex items-start">
                          <label className="flex items-start cursor-pointer group w-full">
                            <input
                              type="checkbox"
                              checked={isChecked || false}
                              onChange={() => toggleDocument(category, docIndex)}
                              className="mr-4 mt-1 w-5 h-5 border-2 border-gray-600 bg-black checked:bg-white checked:border-white appearance-none cursor-pointer relative transition-all duration-200"
                              style={{
                                backgroundImage: isChecked ? "url(\"data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='black' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m13.854 3.646-7.5 7.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6 10.293l7.146-7.147a.5.5 0 0 1 .708.708z'/%3e%3c/svg%3e\")" : 'none'
                              }}
                            />
                            <span className={`text-sm transition-all duration-200 group-hover:text-white font-mono ${
                              isChecked ? 'line-through text-gray-500' : 'text-gray-300'
                            }`}>
                              {doc}
                            </span>
                            {isChecked && (
                              <span className="ml-3 text-white">✅</span>
                            )}
                          </label>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-8 text-center">
          <div className="bg-black border border-gray-600 p-8 hover:border-white transition-all duration-300">
            <h2 className="text-3xl font-bold text-white mb-6 font-serif">OPERATIONAL LINKS</h2>
            <p className="text-gray-300 mb-8 font-mono leading-relaxed">
              Access official channels and support networks for visa processing.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a 
                href="https://www.gov.uk/browse/visas-immigration"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-white text-black px-8 py-4 font-mono font-bold tracking-wider hover:bg-gray-200 transition-all duration-300 border-2 border-white"
              >
                [UK.GOV] OFFICIAL PORTAL
              </a>
              <a 
                href="https://www.vfsglobal.co.uk"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-transparent text-white px-8 py-4 font-mono font-bold tracking-wider border-2 border-white hover:bg-white hover:text-black transition-all duration-300"
              >
                [BIOMETRIC] APPOINTMENT
              </a>
              <Link 
                to="/timeline"
                className="bg-gray-900 text-white px-8 py-4 font-mono font-bold tracking-wider border-2 border-gray-600 hover:border-white transition-all duration-300"
              >
                [TIMELINE] VIEW SCHEDULE
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Employment Page with Noir Theme
const EmploymentPage = () => {
  const [jobsData, setJobsData] = useState({ jobs: [], categories: [], job_types: [] });
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [filters, setFilters] = useState({
    category: 'all',
    job_type: 'all',
    search: ''
  });

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await axios.get(`${API}/api/jobs/listings`);
        setJobsData(response.data);
        setFilteredJobs(response.data.jobs);
      } catch (error) {
        console.error('Error fetching jobs:', error);
        // Fallback data
        const fallbackData = {
          jobs: [
            {
              id: 1,
              title: "Senior Software Engineer",
              company: "Peak Tech Solutions",
              location: "Buxton, Peak District",
              salary: "£45,000 - £65,000",
              job_type: "full-time",
              category: "Technology",
              description: "Leading software development for innovative solutions in the heart of Peak District.",
              requirements: ["5+ years experience", "JavaScript/React", "Node.js", "Remote work experience"],
              benefits: ["Healthcare", "Pension", "Flexible hours", "Remote work"],
              application_url: "https://example.com/apply",
              posted_date: "2024-01-15"
            },
            {
              id: 2,
              title: "Tourism Operations Manager",
              company: "Peak Adventures Ltd",
              location: "Bakewell, Peak District",
              salary: "£35,000 - £42,000",
              job_type: "full-time",
              category: "Tourism",
              description: "Manage tourism operations for outdoor adventure company in Peak District.",
              requirements: ["Tourism experience", "Leadership skills", "First aid certified", "Driver's license"],
              benefits: ["Healthcare", "Staff discounts", "Training budget"],
              application_url: "https://example.com/apply",
              posted_date: "2024-01-12"
            }
          ],
          categories: ["Technology", "Tourism"],
          job_types: ["full-time", "part-time", "contract"]
        };
        setJobsData(fallbackData);
        setFilteredJobs(fallbackData.jobs);
      }
    };
    fetchJobs();
  }, []);

  useEffect(() => {
    let filtered = jobsData.jobs;

    if (filters.category !== 'all') {
      filtered = filtered.filter(job => job.category === filters.category);
    }

    if (filters.job_type !== 'all') {
      filtered = filtered.filter(job => job.job_type === filters.job_type);
    }

    if (filters.search) {
      filtered = filtered.filter(job => 
        job.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        job.company.toLowerCase().includes(filters.search.toLowerCase()) ||
        job.location.toLowerCase().includes(filters.search.toLowerCase())
      );
    }

    setFilteredJobs(filtered);
  }, [filters, jobsData]);

  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const employmentLinks = [
    { name: "INDEED UK", url: "https://uk.indeed.com", description: "Primary job search platform" },
    { name: "REED COMMAND", url: "https://www.reed.co.uk", description: "UK recruitment specialists" },
    { name: "LINKEDIN OPS", url: "https://www.linkedin.com/jobs", description: "Professional networking" },
    { name: "CV GUIDANCE", url: "https://www.gov.uk/cv-tips", description: "UK-specific CV protocols" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 fade-in">
          <h1 className="text-5xl font-bold font-serif text-white mb-6">
            CAREER SEARCH
          </h1>
          <p className="text-xl text-gray-400 mb-8 font-mono tracking-wide">
            [ PEAK DISTRICT OPPORTUNITIES DATABASE ]
          </p>
        </div>

        {/* Employment Resources */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 font-mono text-center tracking-wider">RECRUITMENT NETWORKS</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {employmentLinks.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-black border border-gray-600 p-4 hover:border-white hover:bg-gray-900 transition-all duration-300"
              >
                <h3 className="font-bold text-white mb-2 font-mono tracking-wide">{link.name}</h3>
                <p className="text-gray-400 text-sm font-mono">{link.description}</p>
              </a>
            ))}
          </div>
        </div>

        {/* Filters */}
        <div className="bg-black border border-gray-600 p-8 mb-8 hover:border-white transition-all duration-300">
          <h2 className="text-xl font-bold text-white mb-6 font-mono tracking-wider">SEARCH FILTERS</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-mono text-gray-400 mb-2 tracking-wider">SEARCH</label>
              <input
                type="text"
                placeholder="Job title, company, location..."
                value={filters.search}
                onChange={(e) => updateFilter('search', e.target.value)}
                className="w-full bg-black border-2 border-gray-700 p-3 text-white font-mono focus:border-white focus:outline-none transition-all duration-300"
              />
            </div>
            <div>
              <label className="block text-sm font-mono text-gray-400 mb-2 tracking-wider">CATEGORY</label>
              <select
                value={filters.category}
                onChange={(e) => updateFilter('category', e.target.value)}
                className="w-full bg-black border-2 border-gray-700 p-3 text-white font-mono focus:border-white focus:outline-none transition-all duration-300"
              >
                <option value="all">ALL CATEGORIES</option>
                {jobsData.categories && jobsData.categories.map(category => (
                  <option key={category} value={category}>{category.toUpperCase()}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-mono text-gray-400 mb-2 tracking-wider">TYPE</label>
              <select
                value={filters.job_type}
                onChange={(e) => updateFilter('job_type', e.target.value)}
                className="w-full bg-black border-2 border-gray-700 p-3 text-white font-mono focus:border-white focus:outline-none transition-all duration-300"
              >
                <option value="all">ALL TYPES</option>
                {jobsData.job_types && jobsData.job_types.map(type => (
                  <option key={type} value={type}>{type.replace('-', ' ').toUpperCase()}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilters({ category: 'all', job_type: 'all', search: '' })}
                className="w-full bg-white text-black px-4 py-3 font-mono font-bold tracking-wider hover:bg-gray-200 transition-all duration-300"
              >
                [RESET] CLEAR
              </button>
            </div>
          </div>
          <div className="mt-4 text-center">
            <span className="text-gray-400 font-mono">
              SHOWING {filteredJobs.length} OF {jobsData.jobs.length} POSITIONS
            </span>
          </div>
        </div>

        {/* Job Listings */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredJobs.map(job => (
            <div key={job.id} className="bg-black border border-gray-600 p-8 transition-all duration-300 hover:border-white hover:bg-gray-900">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h3 className="text-xl font-bold text-white mb-2 font-mono tracking-wide">{job.title}</h3>
                  <p className="text-lg text-gray-300 font-mono">{job.company}</p>
                  <p className="text-gray-400 font-mono">📍 {job.location}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white font-mono">{job.salary}</div>
                  <div className="text-sm text-gray-400 font-mono">{job.job_type.replace('-', ' ').toUpperCase()}</div>
                </div>
              </div>

              <p className="text-gray-300 mb-6 leading-relaxed font-mono">{job.description}</p>

              <div className="flex flex-wrap gap-2 mb-6">
                <span className="px-3 py-1 bg-gray-900 border border-gray-700 text-gray-300 text-sm font-mono font-bold tracking-wider">
                  {job.category}
                </span>
                <span className="px-3 py-1 bg-gray-900 border border-gray-700 text-gray-300 text-sm font-mono font-bold tracking-wider">
                  {job.job_type.replace('-', ' ').toUpperCase()}
                </span>
              </div>

              <div className="border-t border-gray-700 pt-6">
                <h4 className="font-semibold text-white mb-3 font-mono tracking-wider">REQUIREMENTS:</h4>
                <ul className="text-sm text-gray-300 space-y-1 mb-6 font-mono">
                  {job.requirements.slice(0, 3).map((req, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-white mr-3">▸</span>
                      {req}
                    </li>
                  ))}
                  {job.requirements.length > 3 && (
                    <li className="text-gray-500 italic font-mono">
                      +{job.requirements.length - 3} more requirements
                    </li>
                  )}
                </ul>

                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-400 font-mono">
                    Posted: {new Date(job.posted_date).toLocaleDateString()}
                  </div>
                  <a
                    href={job.application_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-white text-black px-6 py-2 font-mono font-bold tracking-wider hover:bg-gray-200 transition-all duration-300"
                  >
                    [APPLY] →
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredJobs.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-6">🔍</div>
            <h2 className="text-3xl font-bold text-white mb-4 font-serif">NO POSITIONS FOUND</h2>
            <p className="text-gray-400 font-mono">Adjust search criteria or browse all available positions.</p>
            <button
              onClick={() => setFilters({ category: 'all', job_type: 'all', search: '' })}
              className="mt-6 bg-white text-black px-8 py-3 font-mono font-bold tracking-wider hover:bg-gray-200 transition-all duration-300"
            >
              [SHOW ALL] POSITIONS
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Housing Page with Noir Theme
const HousingPage = () => {
  const [selectedTab, setSelectedTab] = useState('comparison');

  const housingLinks = [
    { name: "RIGHTMOVE", url: "https://www.rightmove.co.uk", description: "Primary property portal" },
    { name: "ZOOPLA INTEL", url: "https://www.zoopla.co.uk", description: "Property search and valuation" },
    { name: "SPAREROOM", url: "https://www.spareroom.co.uk", description: "Room rental platform" },
    { name: "COUNCIL TAX", url: "https://www.gov.uk/council-tax", description: "Tax calculation system" }
  ];

  const comparison = {
    phoenix: {
      name: "Phoenix, Arizona",
      median_price: "$445,000",
      rental_price: "$1,400/month",
      property_tax: "0.6% annually",
      utilities: "$120/month",
      climate: "Desert, hot summers",
      population: "1.7 million",
      pros: ["Warm weather year-round", "Lower cost of living", "No state income tax", "Growing tech sector"],
      cons: ["Extreme summer heat", "Water scarcity concerns", "Urban sprawl", "Limited public transport"]
    },
    peak_district: {
      name: "Peak District, UK",
      median_price: "£285,000",
      rental_price: "£950/month",
      property_tax: "Council Tax varies",
      utilities: "£150/month",
      climate: "Temperate, mild summers",
      population: "38,000 residents",
      pros: ["Stunning natural beauty", "Rich history and culture", "Strong community", "Excellent hiking/outdoor activities"],
      cons: ["Higher living costs", "Limited job market", "Weather can be unpredictable", "Rural location"]
    }
  };

  const propertyTypes = [
    { 
      type: "Traditional Stone Cottage", 
      price: "£200,000 - £400,000", 
      description: "Characteristic Peak District homes with original features",
      features: ["Stone construction", "Original beams", "Open fireplaces", "Garden/outdoor space"]
    },
    { 
      type: "Modern Family Home", 
      price: "£350,000 - £600,000", 
      description: "Contemporary builds with modern amenities",
      features: ["Energy efficient", "Modern kitchen", "Multiple bedrooms", "Parking"]
    },
    { 
      type: "Village Terraced House", 
      price: "£180,000 - £320,000", 
      description: "Traditional terraced homes in village centers",
      features: ["Period features", "Village location", "Walking distance to amenities", "Character property"]
    },
    { 
      type: "Rural Farmhouse", 
      price: "£400,000 - £800,000", 
      description: "Converted farmhouses with substantial grounds",
      features: ["Large plot", "Outbuildings", "Privacy", "Rural views"]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 fade-in">
          <h1 className="text-5xl font-bold font-serif text-white mb-6">
            LOCATION INTEL
          </h1>
          <p className="text-xl text-gray-400 mb-8 font-mono tracking-wide">
            [ HOUSING ANALYSIS & SEARCH PROTOCOLS ]
          </p>
        </div>

        {/* Housing Resources */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 font-mono text-center tracking-wider">PROPERTY NETWORKS</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {housingLinks.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-black border border-gray-600 p-4 hover:border-white hover:bg-gray-900 transition-all duration-300"
              >
                <h3 className="font-bold text-white mb-2 font-mono tracking-wide">{link.name}</h3>
                <p className="text-gray-400 text-sm font-mono">{link.description}</p>
              </a>
            ))}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-gray-900 p-1 border border-gray-700">
            <button
              onClick={() => setSelectedTab('comparison')}
              className={`px-6 py-3 font-mono font-bold tracking-wider transition-all duration-300 ${
                selectedTab === 'comparison'
                  ? 'bg-white text-black'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              [COMPARISON] LOCATIONS
            </button>
            <button
              onClick={() => setSelectedTab('properties')}
              className={`px-6 py-3 font-mono font-bold tracking-wider transition-all duration-300 ${
                selectedTab === 'properties'
                  ? 'bg-white text-black'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              [PROPERTIES] TYPES
            </button>
          </div>
        </div>

        {/* Location Comparison */}
        {selectedTab === 'comparison' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {Object.entries(comparison).map(([key, location]) => (
              <div key={key} className="bg-black border border-gray-600 p-8 hover:border-white transition-all duration-300">
                <h2 className="text-2xl font-bold text-white mb-6 font-mono tracking-wider">{location.name}</h2>
                
                <div className="space-y-4 mb-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-900 border border-gray-700 p-3">
                      <div className="text-sm text-gray-400 font-mono">Median Home Price</div>
                      <div className="text-lg font-bold text-white font-mono">{location.median_price}</div>
                    </div>
                    <div className="bg-gray-900 border border-gray-700 p-3">
                      <div className="text-sm text-gray-400 font-mono">Rental Price</div>
                      <div className="text-lg font-bold text-white font-mono">{location.rental_price}</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-900 border border-gray-700 p-3">
                      <div className="text-sm text-gray-400 font-mono">Property Tax</div>
                      <div className="text-sm font-medium text-gray-300 font-mono">{location.property_tax}</div>
                    </div>
                    <div className="bg-gray-900 border border-gray-700 p-3">
                      <div className="text-sm text-gray-400 font-mono">Utilities</div>
                      <div className="text-sm font-medium text-gray-300 font-mono">{location.utilities}</div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-white mb-2 font-mono tracking-wider">✅ ADVANTAGES</h3>
                    <ul className="space-y-1">
                      {location.pros.map((pro, index) => (
                        <li key={index} className="text-sm text-gray-300 flex items-start font-mono">
                          <span className="text-white mr-3">+</span>
                          {pro}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-white mb-2 font-mono tracking-wider">⚠️ CHALLENGES</h3>
                    <ul className="space-y-1">
                      {location.cons.map((con, index) => (
                        <li key={index} className="text-sm text-gray-300 flex items-start font-mono">
                          <span className="text-gray-500 mr-3">-</span>
                          {con}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Property Types */}
        {selectedTab === 'properties' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {propertyTypes.map((property, index) => (
              <div key={index} className="bg-black border border-gray-600 p-8 hover:border-white transition-all duration-300">
                <h3 className="text-xl font-bold text-white mb-3 font-mono tracking-wider">{property.type}</h3>
                <div className="text-2xl font-bold text-white mb-4 font-mono">{property.price}</div>
                <p className="text-gray-300 mb-6 font-mono">{property.description}</p>
                
                <h4 className="font-semibold text-white mb-3 font-mono tracking-wider">KEY FEATURES:</h4>
                <ul className="space-y-1">
                  {property.features.map((feature, idx) => (
                    <li key={idx} className="text-sm text-gray-300 flex items-start font-mono">
                      <span className="text-white mr-3">▸</span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Logistics Page with Noir Theme
const LogisticsPage = () => {
  const logisticsLinks = [
    { name: "INTERNATIONAL MOVERS", url: "https://www.internationalmovers.com", description: "Global moving services" },
    { name: "CUSTOMS INTEL", url: "https://www.gov.uk/bringing-goods-into-uk-personal-use", description: "UK customs regulations" },
    { name: "SHIPPING CALC", url: "https://www.shipito.com", description: "International shipping calculator" },
    { name: "STORAGE UNITS", url: "https://www.safestore.co.uk", description: "Temporary storage solutions" }
  ];

  const movingCompanies = [
    {
      name: "GLOBAL RELOCATIONS",
      speciality: "International Moves",
      rating: "4.8/5",
      estimate: "$4,500 - $7,000",
      services: ["Full packing", "Customs clearance", "Door-to-door", "Insurance included"]
    },
    {
      name: "PHOENIX TO UK SPECIALISTS",
      speciality: "US-UK Moves",
      rating: "4.6/5",
      estimate: "$3,800 - $6,200",
      services: ["Pet relocation", "Vehicle shipping", "Storage solutions", "24/7 tracking"]
    },
    {
      name: "PEAK DISTRICT MOVERS",
      speciality: "Local Delivery",
      rating: "4.9/5",
      estimate: "$800 - $1,500",
      services: ["Final mile delivery", "Unpacking", "Furniture assembly", "Local expertise"]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 fade-in">
          <h1 className="text-5xl font-bold font-serif text-white mb-6">
            MOVEMENT OPS
          </h1>
          <p className="text-xl text-gray-400 mb-8 font-mono tracking-wide">
            [ INTERNATIONAL LOGISTICS COORDINATION ]
          </p>
        </div>

        {/* Logistics Resources */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 font-mono text-center tracking-wider">LOGISTICS NETWORKS</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {logisticsLinks.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-black border border-gray-600 p-4 hover:border-white hover:bg-gray-900 transition-all duration-300"
              >
                <h3 className="font-bold text-white mb-2 font-mono tracking-wide">{link.name}</h3>
                <p className="text-gray-400 text-sm font-mono">{link.description}</p>
              </a>
            ))}
          </div>
        </div>

        {/* Moving Companies */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-white mb-8 font-serif text-center">MOVING COMPANIES</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {movingCompanies.map((company, index) => (
              <div key={index} className="bg-black border border-gray-600 p-8 hover:border-white transition-all duration-300">
                <h3 className="text-xl font-bold text-white mb-3 font-mono tracking-wider">{company.name}</h3>
                <div className="mb-4">
                  <span className="bg-gray-900 border border-gray-700 text-gray-300 px-3 py-1 text-sm font-mono font-bold tracking-wider">
                    {company.speciality}
                  </span>
                </div>
                <div className="mb-4">
                  <div className="text-2xl font-bold text-white font-mono">{company.estimate}</div>
                  <div className="text-sm text-gray-400 font-mono">Rating: {company.rating}</div>
                </div>
                
                <h4 className="font-semibold text-white mb-3 font-mono tracking-wider">SERVICES:</h4>
                <ul className="space-y-1 mb-6">
                  {company.services.map((service, idx) => (
                    <li key={idx} className="text-sm text-gray-300 flex items-start font-mono">
                      <span className="text-white mr-3">▸</span>
                      {service}
                    </li>
                  ))}
                </ul>
                
                <button className="w-full bg-white text-black px-6 py-3 font-mono font-bold tracking-wider hover:bg-gray-200 transition-all duration-300">
                  [REQUEST] QUOTE
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Cost Calculator */}
        <div className="bg-black border border-gray-600 p-8 hover:border-white transition-all duration-300">
          <h2 className="text-3xl font-bold text-white mb-8 font-serif text-center">COST CALCULATOR</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-gray-900 border border-gray-700 p-6 text-center">
              <div className="text-3xl font-bold text-white mb-2 font-mono">$5,500</div>
              <div className="text-gray-400 text-sm font-mono tracking-wider">ESTIMATED MOVING COST</div>
            </div>
            <div className="bg-gray-900 border border-gray-700 p-6 text-center">
              <div className="text-3xl font-bold text-white mb-2 font-mono">$1,200</div>
              <div className="text-gray-400 text-sm font-mono tracking-wider">SHIPPING COSTS</div>
            </div>
            <div className="bg-gray-900 border border-gray-700 p-6 text-center">
              <div className="text-3xl font-bold text-white mb-2 font-mono">$800</div>
              <div className="text-gray-400 text-sm font-mono tracking-wider">CUSTOMS & FEES</div>
            </div>
            <div className="bg-gray-900 border border-gray-700 p-6 text-center">
              <div className="text-3xl font-bold text-white mb-2 font-mono">4-6</div>
              <div className="text-gray-400 text-sm font-mono tracking-wider">WEEKS TRANSIT</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Analytics Page with Noir Theme
const AnalyticsPage = () => {
  const analyticsData = [
    { metric: "COMPLETION RATE", value: "68%", trend: "+12%", status: "good" },
    { metric: "TIMELINE PROGRESS", value: "24/34", trend: "+5", status: "good" },
    { metric: "BUDGET UTILIZED", value: "$12,400", trend: "+$800", status: "neutral" },
    { metric: "DAYS REMAINING", value: "89", trend: "-7", status: "urgent" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 fade-in">
          <h1 className="text-5xl font-bold font-serif text-white mb-6">
            DATA ANALYSIS
          </h1>
          <p className="text-xl text-gray-400 mb-8 font-mono tracking-wide">
            [ PROGRESS INSIGHTS & METRICS DASHBOARD ]
          </p>
        </div>

        {/* Analytics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {analyticsData.map((data, index) => (
            <div key={index} className="bg-black border border-gray-600 p-8 hover:border-white transition-all duration-300 text-center">
              <h3 className="text-lg font-bold text-white mb-4 font-mono tracking-wider">{data.metric}</h3>
              <div className="text-4xl font-bold text-white mb-2 font-mono">{data.value}</div>
              <div className={`text-sm font-mono ${
                data.status === 'good' ? 'text-green-400' :
                data.status === 'urgent' ? 'text-red-400' : 'text-gray-400'
              }`}>
                {data.trend}
              </div>
            </div>
          ))}
        </div>

        {/* Progress Visualization */}
        <div className="bg-black border border-gray-600 p-8 hover:border-white transition-all duration-300 text-center">
          <h2 className="text-3xl font-bold text-white mb-8 font-serif">MISSION ANALYTICS</h2>
          <p className="text-gray-400 font-mono text-lg leading-relaxed">
            Advanced analytics dashboard with real-time progress tracking, timeline forecasting, 
            and budget analysis coming soon.
          </p>
        </div>
      </div>
    </div>
  );
};

// Resources Page with Noir Theme
const ResourcesPage = () => {
  const [resources, setResources] = useState(null);

  useEffect(() => {
    const fetchResources = async () => {
      try {
        const response = await axios.get(`${API}/api/resources/all`);
        setResources(response.data);
      } catch (error) {
        console.error('Error fetching resources:', error);
        // Fallback data
        setResources({
          visa_legal: [
            { name: "UK Government Visa Guide", url: "https://www.gov.uk/browse/visas-immigration", description: "Official UK visa information" },
            { name: "Immigration Law Society", url: "https://www.lawsociety.org.uk", description: "Find qualified immigration lawyers" }
          ],
          employment: [
            { name: "Indeed UK", url: "https://uk.indeed.com", description: "Primary job search platform" },
            { name: "LinkedIn Jobs", url: "https://www.linkedin.com/jobs", description: "Professional networking and jobs" }
          ],
          housing: [
            { name: "Rightmove", url: "https://www.rightmove.co.uk", description: "UK's largest property portal" },
            { name: "Zoopla", url: "https://www.zoopla.co.uk", description: "Property search and valuation" }
          ]
        });
      }
    };
    fetchResources();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 fade-in">
          <h1 className="text-5xl font-bold font-serif text-white mb-6">
            SUPPORT NETWORK
          </h1>
          <p className="text-xl text-gray-400 mb-8 font-mono tracking-wide">
            [ EXTERNAL RESOURCES & INTELLIGENCE TOOLS ]
          </p>
        </div>

        {resources && Object.entries(resources).map(([category, items], categoryIndex) => (
          <div key={category} className="mb-12">
            <h2 className="text-3xl font-bold text-white mb-8 font-serif text-center capitalize">
              {category.replace('_', ' & ')}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {items.map((resource, index) => (
                <a
                  key={index}
                  href={resource.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-black border border-gray-600 p-6 hover:border-white hover:bg-gray-900 transition-all duration-300 block"
                >
                  <h3 className="font-bold text-white mb-3 font-mono tracking-wide">{resource.name}</h3>
                  <p className="text-gray-400 text-sm font-mono">{resource.description}</p>
                </a>
              ))}
            </div>
          </div>
        ))}

        {!resources && (
          <div className="text-center py-12">
            <div className="text-6xl mb-6">🔗</div>
            <h2 className="text-3xl font-bold text-white mb-4 font-serif">LOADING RESOURCES</h2>
            <p className="text-gray-400 font-mono">Establishing network connections...</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Hacking Animation Login Component
const LoginPage = () => {
  const [currentPhase, setCurrentPhase] = useState('initial'); // initial, hacking, backdoor, authenticating, success
  const [terminalLines, setTerminalLines] = useState([]);
  const [isAnimating, setIsAnimating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [loginUsername, setLoginUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [animationTimeoutId, setAnimationTimeoutId] = useState(null);

  const hackingCommands = [
    "root@relocation-system:~# nmap -sS 192.168.1.1",
    "Starting Nmap scan...",
    "Host is up (0.023s latency)",
    "PORT     STATE SERVICE",
    "22/tcp   open  ssh",
    "443/tcp  open  https",
    "8001/tcp open  unknown",
    "",
    "root@relocation-system:~# hydra -l admin -P wordlist.txt ssh://192.168.1.1",
    "Hydra v9.4 starting...",
    "[SSH] host: 192.168.1.1   login: admin   password: relocate2025",
    "[SSH] Valid credentials found!",
    "",
    "root@relocation-system:~# ssh admin@192.168.1.1",
    "Welcome to RelocateMe Secure Terminal",
    "Last login: Thu Jun  6 02:15:42 2025 from 10.0.0.1",
    "",
    "admin@relocate-server:~$ sudo -l",
    "User admin may run the following commands:",
    "    (ALL : ALL) ALL",
    "",
    "admin@relocate-server:~$ cat /etc/shadow | grep relocate_user",
    "relocate_user:$6$salt$hash:19834:0:99999:7:::",
    "",
    "admin@relocate-server:~$ john --wordlist=passwords.txt shadow.txt",
    "John the Ripper 1.9.0-jumbo-1",
    "Loaded 1 password hash",
    "Press 'q' or Ctrl-C to abort...",
    "SecurePass2025!  (relocate_user)",
    "",
    "admin@relocate-server:~$ echo 'Backdoor installed successfully'",
    "Backdoor installed successfully",
    "",
    "admin@relocate-server:~$ ./backdoor_auth.sh",
    "Initializing backdoor authentication...",
    "Bypassing security protocols...",
    "Injecting authentication tokens...",
    "AUTHENTICATION BYPASS: SUCCESS",
    "",
    "ACCESS GRANTED - WELCOME TO RELOCATE SYSTEM"
  ];

  const typewriterEffect = (lines, callback) => {
    let currentLineIndex = 0;
    let currentCharIndex = 0;
    const currentTerminalLines = [];

    const typeNextChar = () => {
      if (currentLineIndex >= lines.length) {
        console.log("Typewriter animation completed, calling callback");
        callback();
        return;
      }

      const currentLine = lines[currentLineIndex];
      
      if (currentCharIndex >= currentLine.length) {
        currentTerminalLines.push(currentLine);
        setTerminalLines([...currentTerminalLines]);
        currentLineIndex++;
        currentCharIndex = 0;
        // Faster line transition - reduced from 100-300ms to 50-150ms
        setTimeout(typeNextChar, 50 + Math.random() * 100);
      } else {
        const partialLine = currentLine.substring(0, currentCharIndex + 1);
        const displayLines = [...currentTerminalLines, partialLine];
        setTerminalLines(displayLines);
        currentCharIndex++;
        // Much faster character typing - reduced from 20-100ms to 5-15ms
        setTimeout(typeNextChar, 5 + Math.random() * 10);
      }
    };

    typeNextChar();
  };

  const startHackingAnimation = () => {
    setIsAnimating(true);
    setCurrentPhase('hacking');
    setTerminalLines([]);
    
    // Add a timeout safety net in case animation gets stuck
    const timeoutId = setTimeout(() => {
      console.log("Animation timeout reached, forcing completion");
      setCurrentPhase('success');
      setTimeout(() => {
        setShowForm(true);
      }, 1000);
    }, 15000); // 15 second timeout
    
    setAnimationTimeoutId(timeoutId);
    
    typewriterEffect(hackingCommands, () => {
      clearTimeout(timeoutId);
      console.log("Animation completed normally");
      setTimeout(() => {
        setCurrentPhase('success');
        setTimeout(() => {
          setShowForm(true);
        }, 2000);
      }, 1000);
    });
  };

  const skipAnimation = () => {
    if (animationTimeoutId) {
      clearTimeout(animationTimeoutId);
    }
    setCurrentPhase('success');
    setTimeout(() => {
      setShowForm(true);
    }, 500);
  };

  const handleRealLogin = async (e) => {
    e.preventDefault();
    setCurrentPhase('authenticating');

    // Use the credentials that were "discovered" by the hack
    const hackUsername = "relocate_user";
    const hackPassword = "SecurePass2025!";

    try {
      const response = await axios.post(`${API}/api/auth/login`, {
        username: hackUsername,
        password: hackPassword
      });

      if (response.data && response.data.access_token) {
        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("username", hackUsername);
        setCurrentPhase('success');
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } else {
        setError("Authentication failed");
        setCurrentPhase('initial');
        setShowForm(false);
      }
    } catch (err) {
      setError("System breach unsuccessful");
      console.error("Login error:", err);
      setCurrentPhase('initial');
      setShowForm(false);
    }
  };

  if (currentPhase === 'initial') {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-6 relative overflow-hidden">
        {/* Film noir background with subtle texture */}
        <div className="absolute inset-0 opacity-10 bg-gradient-to-br from-gray-900 via-black to-gray-800"></div>
        
        <div className="max-w-2xl w-full bg-black border-2 border-white p-8 shadow-2xl relative z-10">
          <div className="text-center mb-8">
            <h1 className="text-5xl font-bold text-white mb-4 font-serif noir-title">
              RELOCATE.SYS
            </h1>
            <p className="text-gray-300 font-mono text-lg tracking-wider">
              [ UNAUTHORIZED ACCESS DETECTED ]
            </p>
            <p className="text-gray-500 font-mono text-sm mt-2">
              SECURITY BREACH IMMINENT - INITIATE COUNTERMEASURES
            </p>
          </div>

          {error && (
            <div className="bg-red-900 border border-red-400 text-red-200 p-4 mb-6 font-mono text-sm animate-pulse">
              ⚠️ {error}
            </div>
          )}

          <div className="text-center">
            <button
              onClick={startHackingAnimation}
              className="hoverable primary-button"
            >
              [ INITIATE SYSTEM BREACH ]
            </button>
            <p className="text-gray-400 font-mono text-xs mt-4 opacity-75">
              WARNING: Unauthorized access is illegal
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (currentPhase === 'hacking' || currentPhase === 'backdoor') {
    return (
      <div className="min-h-screen bg-black p-4 font-mono text-white overflow-hidden">
        <div className="max-w-6xl mx-auto relative">
          <div className="border-2 border-white bg-black p-6 h-screen overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                <div className="w-3 h-3 bg-gray-400 rounded-full mr-4"></div>
                <span className="text-gray-300 text-sm">BREACH_TERMINAL_v2.5.0</span>
              </div>
              <button
                onClick={skipAnimation}
                className="hoverable"
              >
                SKIP ANIMATION
              </button>
            </div>
            
            <div className="space-y-1">
              {terminalLines.map((line, index) => (
                <div key={index} className="flex">
                  <span className="text-gray-400 mr-2">$</span>
                  <span className={line.includes('SUCCESS') || line.includes('GRANTED') ? 'text-white font-bold' : 
                                line.includes('ERROR') || line.includes('FAILED') ? 'text-red-400' :
                                line.includes('Valid credentials') || line.includes('Backdoor') || line.includes('SecurePass2025!') ? 'text-red-300' : 'text-gray-300'}
                  >
                    {line}
                  </span>
                </div>
              ))}
              <div className="flex">
                <span className="text-gray-400 mr-2">$</span>
                <span className="animate-pulse text-white">█</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (currentPhase === 'success' && !showForm) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-6">
        <div className="text-center">
          <div className="text-8xl text-white font-mono mb-8 animate-pulse">
            ✓
          </div>
          <h1 className="text-4xl font-bold text-white mb-4 font-mono">
            ACCESS GRANTED
          </h1>
          <p className="text-gray-300 font-mono text-xl">
            Backdoor authentication successful
          </p>
          <p className="text-gray-500 font-mono text-sm mt-2">
            Credentials extracted: <span className="text-red-300">relocate_user / SecurePass2025!</span>
          </p>
        </div>
      </div>
    );
  }

  if (showForm || currentPhase === 'authenticating') {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-gray-900 border-2 border-white p-8 shadow-2xl">
          <div className="text-center mb-8">
            <div className="text-4xl text-white mb-4">🔓</div>
            <h1 className="text-3xl font-bold text-white mb-2 font-mono">BACKDOOR ACTIVE</h1>
            <p className="text-gray-300 font-mono text-sm">Using compromised credentials</p>
          </div>

          <form onSubmit={handleRealLogin}>
            <div className="mb-6">
              <label className="block text-gray-300 mb-2 font-mono text-sm tracking-wider">EXTRACTED USERNAME</label>
              <input
                type="text"
                value="relocate_user"
                disabled
                className="w-full bg-black border-2 border-gray-500 p-3 text-white font-mono opacity-75"
              />
            </div>

            <div className="mb-8">
              <label className="block text-gray-300 mb-2 font-mono text-sm tracking-wider">CRACKED PASSWORD</label>
              <input
                type="password"
                value="SecurePass2025!"
                disabled
                className="w-full bg-black border-2 border-gray-500 p-3 text-red-300 font-mono opacity-75"
              />
            </div>

            <button
              type="submit"
              disabled={currentPhase === 'authenticating'}
              className="hoverable primary-button w-full disabled:opacity-50"
            >
              {currentPhase === 'authenticating' ? "EXECUTING BACKDOOR..." : "AUTHENTICATE WITH BACKDOOR"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-500 font-mono text-xs">
              ⚠️ UNAUTHORIZED ACCESS DETECTED ⚠️
            </p>
            <p className="text-red-300 font-mono text-xs mt-1">
              RELOCATE.SYS COMPROMISED
            </p>
          </div>
        </div>
      </div>
    );
  }
};

// Main App Component
const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [currentPath, setCurrentPath] = useState("/dashboard");

  // Check if user is already logged in
  useEffect(() => {
    // Check for logout parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('logout') === 'true') {
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      setIsLoggedIn(false);
      setUsername("");
      console.log("Forced logout via URL parameter");
      // Remove the parameter from URL
      window.history.replaceState({}, document.title, window.location.pathname);
      return;
    }

    const token = localStorage.getItem("token");
    const storedUsername = localStorage.getItem("username");
    console.log("Checking login status:", { token: !!token, username: storedUsername });
    if (token && storedUsername) {
      setIsLoggedIn(true);
      setUsername(storedUsername);
      console.log("User is logged in, showing main app");
    } else {
      console.log("User is not logged in, showing login animation");
    }
  }, []);

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setIsLoggedIn(false);
    setUsername("");
  };

  // Update current path when location changes
  const AppContent = () => {
    const location = useLocation();

    useEffect(() => {
      setCurrentPath(location.pathname);
    }, [location]);

    return (
      <>
        <SpyCursor />
        <Navigation user={username} onLogout={handleLogout} currentPath={currentPath} />
        <Routes>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/timeline" element={<TimelinePage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/visa" element={<VisaPage />} />
          <Route path="/employment" element={<EmploymentPage />} />
          <Route path="/housing" element={<HousingPage />} />
          <Route path="/logistics" element={<LogisticsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/resources" element={<ResourcesPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </>
    );
  };

  return (
    <Router>
      {isLoggedIn ? <AppContent /> : <LoginPage />}
      {isLoggedIn && <MissionDebriefButton />}
    </Router>
  );
};

export default App;