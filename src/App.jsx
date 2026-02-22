import React, { useState, useEffect } from 'react';
import { UtensilsCrossed, Leaf, ScanLine, Download, X } from 'lucide-react';
import FoodCompatibility from './FoodCompatibility';
import PrescriptionScanner from './PrescriptionScanner';
import '../index.css';

const API_URL = 'http://localhost:8002';

// Helper functions and styles (defined once outside App component)
const getColorForLevel = (level) => {
  if (level.includes("High")) return "#00ff88"; // Green
  if (level.includes("Low")) return "#ff2e63"; // Red
  return "#ffcc00"; // Yellow
};

const navButtonStyle = {
  display: 'flex',
  alignItems: 'center',
  padding: '10px 20px',
  borderRadius: '30px',
  border: '1px solid transparent',
  cursor: 'pointer',
  color: 'white',
  fontSize: '1rem',
  fontWeight: '600',
  transition: 'all 0.3s ease'
};

export default function App() {
  // Get URL parameters for PWA shortcuts
  const urlParams = new URLSearchParams(window.location.search);
  const initialTab = urlParams.get('tab') || 'check';

  const [activeTab, setActiveTab] = useState(initialTab);

  // PWA Install Prompt
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);

  // PWA Install Prompt handling
  useEffect(() => {
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallPrompt(true);
    };

    const handleAppInstalled = () => {
      setDeferredPrompt(null);
      setShowInstallPrompt(false);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      console.log('User accepted the install prompt');
    } else {
      console.log('User dismissed the install prompt');
    }

    setDeferredPrompt(null);
    setShowInstallPrompt(false);
  };

  const handleModeSwitch = (mode) => {
    setActiveTab(mode);
    // Note: Child components manage their own state clearing when `activeTab` changes
  };

  return (
    <div className="container" style={{ maxWidth: '800px', width: '100%' }}>
      {/* PWA Install Prompt */}
      {showInstallPrompt && (
        <div style={{
          position: 'fixed',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '15px 20px',
          borderRadius: '12px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
          zIndex: 10000,
          display: 'flex',
          alignItems: 'center',
          gap: '15px',
          maxWidth: '90vw',
          fontSize: '14px'
        }}>
          <Download size={20} />
          <div>
            <strong>Install NutriSync AI</strong>
            <br />
            Get the full app experience on your device!
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={handleInstallClick}
              style={{
                background: '#00ff88',
                color: '#000',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              Install
            </button>
            <button
              onClick={() => setShowInstallPrompt(false)}
              style={{
                background: 'transparent',
                color: 'white',
                border: '1px solid rgba(255,255,255,0.3)',
                padding: '8px 12px',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              <X size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <header style={{ textAlign: 'center', marginBottom: '30px' }} className="fade-in">
        <h1 style={{ fontSize: '3rem', marginBottom: '10px' }} className="title-gradient">NutriSync AI</h1>
        <p style={{ opacity: 0.8 }}>Powered by Machine Learning & Nutritional Science</p>
      </header>

      {/* Navigation */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '30px' }} className="fade-in">
        <button
          onClick={() => handleModeSwitch('check')}
          style={{ ...navButtonStyle, background: activeTab === 'check' ? 'rgba(0, 198, 255, 0.2)' : 'rgba(255,255,255,0.05)', borderColor: activeTab === 'check' ? '#00c6ff' : 'transparent' }}
        >
          <UtensilsCrossed size={24} color={activeTab === 'check' ? '#00c6ff' : 'white'} />
          <span style={{ marginLeft: '10px' }}>Food Compatibility</span>
        </button>

        <button
          onClick={() => handleModeSwitch('suggest')}
          style={{ ...navButtonStyle, background: activeTab === 'suggest' ? 'rgba(0, 255, 136, 0.2)' : 'rgba(255,255,255,0.05)', borderColor: activeTab === 'suggest' ? '#00ff88' : 'transparent' }}
        >
          <Leaf size={24} color={activeTab === 'suggest' ? '#00ff88' : 'white'} />
          <span style={{ marginLeft: '10px' }}>AI Suggestions</span>
        </button>

        <button
          onClick={() => handleModeSwitch('scan')}
          style={{ ...navButtonStyle, background: activeTab === 'scan' ? 'rgba(255, 136, 0, 0.2)' : 'rgba(255,255,255,0.05)', borderColor: activeTab === 'scan' ? '#ff8800' : 'transparent' }}
        >
          <ScanLine size={24} color={activeTab === 'scan' ? '#ff8800' : 'white'} />
          <span style={{ marginLeft: '10px' }}>Prescription Scanner</span>
        </button>
      </div>

      {/* Main Content Based on Active Tab */}
      {activeTab === 'check' && <FoodCompatibility activeTab={activeTab} />}
      {activeTab === 'suggest' && <FoodCompatibility activeTab={activeTab} />}
      {activeTab === 'scan' && <PrescriptionScanner />}

    </div>
  );
}
