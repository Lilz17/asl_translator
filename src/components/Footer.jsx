import React from 'react';
import { useTranslation } from '../context/TranslationContext';
import { Sparkles, Globe, Heart, ShieldAlert } from 'lucide-react';

const Footer = () => {
  const { selectedLanguage } = useTranslation();

  return (
    <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 py-10 px-4 sm:px-6 lg:px-8 mt-auto z-10">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 pb-8 border-b border-slate-800 text-sm">
        {/* Info Column */}
        <div className="space-y-3.5">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
              SB
            </div>
            <span className="font-extrabold text-white text-base tracking-tight">SignBridge / ASL Translator</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            {selectedLanguage === 'hi'
              ? 'वास्तविक समय में साइन ट्रांसलेशन के माध्यम से संचार बाधाओं को तोड़ना। पहुंच और समावेश के लिए निर्मित।'
              : 'Breaking communication barriers through real-time sign translation. Engineered with computer vision and accessibility-first principles.'}
          </p>
        </div>

        {/* Tech Stack Column */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            {selectedLanguage === 'hi' ? 'तकनीकी स्टैक' : 'Technical Architecture'}
          </h4>
          <div className="flex flex-wrap gap-2 text-xs">
            {['React 19', 'Tailwind CSS v4', 'MediaPipe Hands', 'HTML5 Web Media APIs', 'Speech Synthesis', 'Context API'].map((tech) => (
              <span key={tech} className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 text-slate-300 font-medium">
                {tech}
              </span>
            ))}
          </div>
        </div>

        {/* Team Column */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            {selectedLanguage === 'hi' ? 'परियोजना दर्शन' : 'Mission & Development'}
          </h4>
          <p className="text-xs text-slate-400 leading-relaxed flex items-center">
            <Heart className="w-4.5 h-4.5 mr-2 text-rose-500 shrink-0 fill-rose-500" />
            <span>
              {selectedLanguage === 'hi' 
                ? 'हाथ के संकेतों को तत्काल समझने और बोले गए शब्दों में बदलने के लिए आधुनिक तकनीकों का उपयोग।' 
                : 'Empowering deaf and hard-of-hearing individuals with immediate verbal broadcast tools.'}
            </span>
          </p>
          <div className="text-xs text-slate-500 flex items-center">
            <ShieldAlert className="w-4 h-4 mr-1 text-slate-600" />
            <span>WCAG 2.1 AA Compliant UI Pattern</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
        <p>
          © 2026 SignBridge. Developed for global accessibility.
        </p>
        <div className="flex space-x-4 mt-3 sm:mt-0">
          <a href="#" className="hover:text-blue-400 transition">Terms of Service</a>
          <span>•</span>
          <a href="#" className="hover:text-blue-400 transition">Accessibility Statement</a>
          <span>•</span>
          <a href="#" className="hover:text-blue-400 transition">Privacy Policy</a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
