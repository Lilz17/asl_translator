import React from 'react';
import { useTranslation } from '../context/TranslationContext';
import WebcamFeed from '../components/WebcamFeed';
import TranslationBox from '../components/TranslationBox';
import HistoryPanel from '../components/HistoryPanel';
import EmergencyButtons from '../components/EmergencyButtons';
import { motion } from 'framer-motion';
import { Sparkles, Info, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const Translate = () => {
  const { selectedLanguage, cameraStatus } = useTranslation();

  // Framer Motion entry animations
  const pageVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.5, staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } }
  };

  return (
    <motion.div 
      variants={pageVariants}
      initial="hidden"
      animate="visible"
      className="py-6 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto flex-grow space-y-6"
    >
      
      {/* Header Navigation */}
      <motion.div 
        variants={itemVariants}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-100 pb-4 text-left"
      >
        <div className="space-y-1">
          {/* Back to mode selection */}
          <Link to="/" className="inline-flex items-center text-xs font-bold text-blue-600 hover:text-blue-700 hover:underline transition mb-1 cursor-pointer">
            <ArrowLeft className="w-3.5 h-3.5 mr-1" />
            <span>{selectedLanguage === 'hi' ? 'मोड चयन पर वापस जाएं' : 'Back to Mode Selection'}</span>
          </Link>
          
          <h2 className="text-xl sm:text-2xl font-black text-slate-800 tracking-tight m-0">
            {selectedLanguage === 'hi' ? 'संकेत → आवाज अनुवादक' : 'ASL → Speech Translator'}
          </h2>
          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest leading-none">
            {selectedLanguage === 'hi' 
              ? 'कैमरे के सामने संकेत करें, अनुवाद स्वतः किया जाएगा।' 
              : 'Perform signs in front of the camera to translate directly to spoken audio.'}
          </p>
        </div>

        {/* Status indicator */}
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full border border-blue-50 bg-blue-50/50 text-[10px] font-extrabold text-blue-600 shadow-2xs self-start sm:self-auto shrink-0">
          <Sparkles className="w-3.5 h-3.5 text-blue-500 animate-pulse" />
          <span>
            {cameraStatus === 'active'
              ? (selectedLanguage === 'hi' ? 'सक्रिय पहचान चालू' : 'REAL-TIME TRACKING ACTIVE')
              : (selectedLanguage === 'hi' ? 'कैमरा बंद' : 'CAMERA OFFLINE')}
          </span>
        </div>
      </motion.div>

      {/* Main Focus Area: Single Center-Focused Translation Stack */}
      <div className="space-y-5">
        
        {/* Step 1: Massive Centered Webcam Hero (Main focus, takes maximum visual space) */}
        <motion.div variants={itemVariants} className="w-full">
          <WebcamFeed />
        </motion.div>

        {/* Step 2: Google Translate style Output Container (Directly below the Webcam) */}
        <motion.div variants={itemVariants} className="w-full">
          <TranslationBox />
        </motion.div>

        {/* Step 3: Horizontal Emergency quick actions pill bar */}
        <motion.div variants={itemVariants} className="w-full">
          <EmergencyButtons />
        </motion.div>

        {/* Step 4: Horizontal stream of Recent Translations */}
        <motion.div variants={itemVariants} className="w-full">
          <HistoryPanel />
        </motion.div>

      </div>

      {/* Accessibilities and data compliance banner */}
      <motion.div 
        variants={itemVariants}
        className="max-w-3xl mx-auto flex items-start space-x-2.5 p-4 rounded-2xl bg-blue-50/20 border border-blue-100/30 text-left text-[11px] text-slate-400 font-semibold"
      >
        <Info className="w-4.5 h-4.5 text-blue-500 shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <b>How to Translate:</b> Enable your camera and position your hand inside the scanning grid. 
          The computer vision landmark system automatically identifies gestured signs, outputs them inside the detected box, and synthesizes natural audio output. 
          Use the <b>Vision Payload Emulator</b> inside the Output Box to simulate gestures if no webcam is connected.
        </p>
      </motion.div>

    </motion.div>
  );
};

export default Translate;
