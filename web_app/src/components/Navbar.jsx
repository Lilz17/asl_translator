import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from '../context/TranslationContext';
import { Camera, Settings, Sparkles, History, Volume2, VolumeX, Menu, X, Landmark } from 'lucide-react';

const Navbar = () => {
  const { 
    cameraStatus, 
    isSpeechEnabled, 
    setIsSpeechEnabled,
    selectedLanguage 
  } = useTranslation();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const isActive = (path) => location.pathname === path;

  const links = [
    { name: selectedLanguage === 'hi' ? 'मुख्य पृष्ठ' : 'Home', path: '/' },
    { 
      name: selectedLanguage === 'hi' ? 'अनुवाद डैशबोर्ड' : 'Dashboard', 
      path: '/translate', 
      icon: <Camera className="w-4 h-4 mr-1.5" /> 
    },
    { 
      name: selectedLanguage === 'hi' ? 'सेटिंग्स' : 'Settings', 
      path: '/settings', 
      icon: <Settings className="w-4 h-4 mr-1.5" /> 
    },
  ];


  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-slate-200/80 px-4 sm:px-6 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo */}
        <Link 
          to="/" 
          className="flex items-center space-x-2.5 group accessible-focus rounded-lg p-1"
          aria-label="SignBridge Home"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform duration-300">
            <span className="font-bold text-lg tracking-wider">SB</span>
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-blue-600 via-indigo-600 to-indigo-700 bg-clip-text text-transparent m-0 p-0 leading-tight">
              SignBridge
            </h1>
            <p className="text-[10px] uppercase font-bold tracking-widest text-slate-400 m-0 p-0">
              {selectedLanguage === 'hi' ? 'ए.एस.एल अनुवादक' : 'ASL Translator'}
            </p>
          </div>
        </Link>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center space-x-1.5">
          {links.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`flex items-center px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 accessible-focus ${
                isActive(link.path)
                  ? 'bg-blue-50 text-blue-600 shadow-sm shadow-blue-500/5 font-semibold'
                  : 'text-slate-600 hover:text-blue-600 hover:bg-slate-50'
              }`}
            >
              {link.icon}
              {link.name}
            </Link>
          ))}
        </div>

        {/* Action Controls */}
        <div className="hidden md:flex items-center space-x-3">
          {/* Quick Voice Output Toggle */}
          <button
            onClick={() => setIsSpeechEnabled(!isSpeechEnabled)}
            className={`p-2.5 rounded-xl border transition-all duration-200 accessible-focus cursor-pointer ${
              isSpeechEnabled 
                ? 'bg-emerald-50 border-emerald-200/80 text-emerald-600 hover:bg-emerald-100' 
                : 'bg-slate-50 border-slate-200 text-slate-400 hover:bg-slate-100'
            }`}
            title={isSpeechEnabled ? 'Mute Speech' : 'Unmute Speech'}
            aria-label={isSpeechEnabled ? 'Mute Voice Output' : 'Enable Voice Output'}
          >
            {isSpeechEnabled ? <Volume2 className="w-4.5 h-4.5" /> : <VolumeX className="w-4.5 h-4.5" />}
          </button>

          {/* System Status Pill */}
          <div className="flex items-center px-3 py-1.5 rounded-full border border-slate-200/80 bg-slate-50 text-xs font-semibold text-slate-600">
            <span className={`w-2 h-2 rounded-full mr-2 ${
              cameraStatus === 'active' 
                ? 'bg-emerald-500 animate-pulse' 
                : cameraStatus === 'loading' 
                ? 'bg-amber-400 animate-pulse' 
                : 'bg-slate-400'
            }`} />
            {cameraStatus === 'active' 
              ? (selectedLanguage === 'hi' ? 'सक्रिय' : 'Live Translation') 
              : cameraStatus === 'loading' 
              ? (selectedLanguage === 'hi' ? 'चालू हो रहा है...' : 'Initializing...') 
              : (selectedLanguage === 'hi' ? 'कैमरा बंद' : 'Camera Ready')}
          </div>
        </div>

        {/* Mobile Menu Button */}
        <div className="md:hidden flex items-center space-x-2">
          <button
            onClick={() => setIsSpeechEnabled(!isSpeechEnabled)}
            className={`p-2 rounded-lg border cursor-pointer ${
              isSpeechEnabled ? 'bg-emerald-50 border-emerald-200 text-emerald-600' : 'bg-slate-50 border-slate-200 text-slate-400'
            }`}
          >
            {isSpeechEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 accessible-focus cursor-pointer"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Panel */}
      {mobileMenuOpen && (
        <div className="md:hidden mt-3 pt-3 border-t border-slate-100 space-y-1 animate-fadeIn">
          {links.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setMobileMenuOpen(false)}
              className={`flex items-center px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive(link.path)
                  ? 'bg-blue-50 text-blue-600 font-semibold'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              {link.icon}
              <span className="ml-2">{link.name}</span>
            </Link>
          ))}
          <div className="pt-2.5 pb-1 border-t border-slate-100 flex items-center justify-between px-4">
            <span className="text-xs text-slate-500 font-medium">Status</span>
            <div className="flex items-center px-2.5 py-1 rounded-full border border-slate-200 bg-slate-50 text-xs font-semibold text-slate-600">
              <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
                cameraStatus === 'active' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'
              }`} />
              {cameraStatus === 'active' ? 'Live' : 'Off'}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
