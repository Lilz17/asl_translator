import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useTranslation } from '../context/TranslationContext';
import { Camera, Volume2, ShieldAlert, History, ArrowRight, Sparkles } from 'lucide-react';

const Home = () => {
  const { selectedLanguage } = useTranslation();

  // Sequential fade-in transition states
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { duration: 0.6, staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  return (
    <div className="relative min-h-[calc(100vh-70px)] bg-gradient-to-tr from-blue-50/25 via-white to-purple-50/25 flex items-center justify-center px-4 overflow-hidden">
      
      {/* Soft floating background light blobs */}
      <div className="absolute inset-0 bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] [background-size:24px_24px] opacity-40 pointer-events-none" />
      <div className="absolute top-1/4 left-1/10 w-[26rem] h-[26rem] bg-blue-300/10 rounded-full filter blur-[120px] pointer-events-none animate-pulse-slow" />
      <div className="absolute bottom-1/4 right-1/10 w-[24rem] h-[24rem] bg-purple-300/10 rounded-full filter blur-[120px] pointer-events-none animate-pulse-slow" />

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-3xl w-full text-center space-y-6 relative z-10 py-6"
      >
        {/* Sparkle Badge */}
        <motion.div 
          variants={itemVariants} 
          className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full border border-blue-100 bg-blue-50/50 text-[10px] font-black uppercase tracking-widest text-blue-600 shadow-2xs"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{selectedLanguage === 'hi' ? 'रीयल-टाइम ए.एस.एल अनुवादक' : 'REAL-TIME ASL TRANSLATOR'}</span>
        </motion.div>

        {/* Hero Section Title */}
        <div className="space-y-3.5 text-center">
          <motion.h1 
            variants={itemVariants}
            className="text-4xl sm:text-6xl font-black tracking-tight text-slate-900 leading-[1.12] m-0"
          >
            SignBridge / <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">ASL Translator</span>
          </motion.h1>
          
          <motion.p 
            variants={itemVariants}
            className="text-slate-500 text-sm sm:text-base font-semibold max-w-xl mx-auto leading-relaxed"
          >
            {selectedLanguage === 'hi'
              ? 'वास्तविक समय में सांकेतिक अनुवाद के माध्यम से संचार बाधाओं को दूर करना। अपना वेबकैम चालू करें और बातचीत शुरू करें।'
              : 'Breaking communication barriers through real-time sign translation. Activate your camera feed and translate gestures directly to vocal speech.'}
          </motion.p>
        </div>

        {/* Primary CTA (Direct path to Dashboard) */}
        <motion.div 
          variants={itemVariants}
          className="pt-1 flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            to="/translate"
            className="group relative inline-flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm px-9 py-4.5 rounded-2xl shadow-md hover:shadow-blue-500/15 active:scale-[0.98] transition cursor-pointer"
          >
            <span>{selectedLanguage === 'hi' ? 'अनुवाद शुरू करें' : 'Start Translation'}</span>
            <ArrowRight className="w-4.5 h-4.5 ml-2 group-hover:translate-x-1 transition-transform" />
          </Link>
        </motion.div>

        {/* Features Matrix Grid */}
        <motion.div 
          variants={itemVariants}
          className="pt-5 border-t border-slate-100 grid grid-cols-2 md:grid-cols-4 gap-4 text-left max-w-2xl mx-auto"
        >
          {/* Card 1: Camera vision */}
          <div className="p-4 rounded-2xl bg-white border border-slate-100 shadow-2xs space-y-2">
            <div className="w-8 h-8 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
              <Camera className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-black text-slate-800 tracking-tight leading-none">Real-Time Tracking</h4>
              <p className="text-[10px] text-slate-400 mt-1 leading-normal font-semibold">Instant landmark overlay mapping hand joint skeletons.</p>
            </div>
          </div>

          {/* Card 2: Audio speech */}
          <div className="p-4 rounded-2xl bg-white border border-slate-100 shadow-2xs space-y-2">
            <div className="w-8 h-8 rounded-xl bg-purple-50 border border-purple-100 flex items-center justify-center text-purple-600">
              <Volume2 className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-black text-slate-800 tracking-tight leading-none">Speech Synthesis</h4>
              <p className="text-[10px] text-slate-400 mt-1 leading-normal font-semibold">Synthesized vocals reading phrases out loud automatically.</p>
            </div>
          </div>

          {/* Card 3: Emergency pills */}
          <div className="p-4 rounded-2xl bg-white border border-slate-100 shadow-2xs space-y-2">
            <div className="w-8 h-8 rounded-xl bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-black text-slate-800 tracking-tight leading-none">Quick Assistance</h4>
              <p className="text-[10px] text-slate-400 mt-1 leading-normal font-semibold">Immediate horizontal pill actions for critical care broadcast.</p>
            </div>
          </div>

          {/* Card 4: Historical log */}
          <div className="p-4 rounded-2xl bg-white border border-slate-100 shadow-2xs space-y-2">
            <div className="w-8 h-8 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
              <History className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-black text-slate-800 tracking-tight leading-none">Chronology Streams</h4>
              <p className="text-[10px] text-slate-400 mt-1 leading-normal font-semibold">Compact horizontal dot list saving previous spoken phrases.</p>
            </div>
          </div>
        </motion.div>

      </motion.div>
    </div>
  );
};

export default Home;
