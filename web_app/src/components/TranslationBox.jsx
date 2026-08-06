import React from 'react';
import { useTranslation } from '../context/TranslationContext';
import { predictGesture } from '../services/api';
import { Volume2, Bookmark, Check, Sparkles, Terminal } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const TranslationBox = () => {
  const {
    detectedText,
    detectedSign,
    confidence,
    selectedLanguage,
    saveCurrentTranslation,
    clearOutput,
    speakText,
    cameraStatus,
    setDetectedText,
    setDetectedSign,
    setConfidence,
    SIGN_DATABASE,
    isProcessing,
    setIsProcessing
  } = useTranslation();

  const [savedSuccess, setSavedSuccess] = React.useState(false);

  const handleSpeak = () => speakText(detectedText);

  const handleSave = () => {
    if (!detectedText) return;
    saveCurrentTranslation();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2000);
  };

  const handleSimulateGesture = (gesture, translation, conf) => {
    setIsProcessing(true);
    setTimeout(() => {
      setDetectedSign(gesture);
      setDetectedText(translation);
      setConfidence(conf);
      setIsProcessing(false);
    }, 650);
  };

  const handleBackendPrediction = async () => {
    try {
      setIsProcessing(true);
      const data = await predictGesture();
      setDetectedSign(data.gesture);
      setDetectedText(data.gesture);
      setConfidence(data.confidence);
      setIsProcessing(false);
    } catch (err) {
      console.log(err);
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-4">

      {/* Main Translation Output */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-5">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`w-2.5 h-2.5 rounded-full ${
              cameraStatus === 'active' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300'
            }`} />
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">
              {selectedLanguage === 'hi' ? 'लाइव अनुवाद आउटपुट' : 'Live Translation Output'}
            </span>
          </div>
          {confidence > 0 && (
            <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
              confidence >= 80
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : confidence >= 60
                ? 'bg-amber-50 text-amber-700 border border-amber-200'
                : 'bg-rose-50 text-rose-700 border border-rose-200'
            }`}>
              {confidence}% {selectedLanguage === 'hi' ? 'सटीकता' : 'confidence'}
            </span>
          )}
        </div>

        {/* Detected Sign Display */}
        <div className="text-center py-6">
          <AnimatePresence mode="wait">
            {isProcessing ? (
              <motion.div
                key="processing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center justify-center space-x-2"
              >
                <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-slate-600 text-sm font-medium">
                  {selectedLanguage === 'hi' ? 'विश्लेषण हो रहा है...' : 'Analysing...'}
                </span>
              </motion.div>
            ) : detectedSign ? (
              <motion.div
                key={detectedSign}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                <div className="text-7xl font-black tracking-tight bg-gradient-to-br from-blue-600 to-indigo-700 bg-clip-text text-transparent leading-none mb-2">
                  {detectedSign}
                </div>
                {detectedText && detectedText !== detectedSign && (
                  <p className="text-slate-700 text-base font-semibold mt-2">{detectedText}</p>
                )}
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center space-y-2"
              >
                <div className="text-5xl font-black text-slate-300">—</div>
                <p className="text-xs font-medium text-slate-400">
                  {selectedLanguage === 'hi'
                    ? 'कैमरा चालू करें और साइन करें'
                    : 'Activate camera and sign to translate'}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Action Buttons */}
        {detectedText && (
          <div className="flex items-center justify-center space-x-2 pt-2 border-t border-slate-100">
            <button
              onClick={handleSpeak}
              className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 text-xs font-bold transition cursor-pointer"
            >
              <Volume2 className="w-3.5 h-3.5" />
              <span>{selectedLanguage === 'hi' ? 'बोलें' : 'Speak'}</span>
            </button>

            <button
              onClick={handleSave}
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl border text-xs font-bold transition cursor-pointer ${
                savedSuccess
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                  : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
              }`}
            >
              {savedSuccess
                ? <><Check className="w-3.5 h-3.5" /><span>{selectedLanguage === 'hi' ? 'सहेजा गया' : 'Saved'}</span></>
                : <><Bookmark className="w-3.5 h-3.5" /><span>{selectedLanguage === 'hi' ? 'सहेजें' : 'Save'}</span></>
              }
            </button>

            <button
              onClick={clearOutput}
              className="px-4 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-bold transition cursor-pointer"
            >
              {selectedLanguage === 'hi' ? 'साफ़ करें' : 'Clear'}
            </button>
          </div>
        )}
      </div>

      {/* Vision Payload Emulator */}
      <div className="bg-slate-50/50 border border-slate-100 rounded-3xl p-4">
        <div className="flex items-center space-x-1.5 border-b border-slate-100 pb-2 mb-2.5">
          <Terminal className="w-3.5 h-3.5 text-indigo-500" />
          <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">
            Vision Payload Emulator
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5 justify-center">
          <button
            onClick={handleBackendPrediction}
            className="px-3 py-2 rounded-lg bg-blue-600 text-white text-xs font-bold"
          >
            Test FastAPI
          </button>

          {(SIGN_DATABASE[selectedLanguage] || SIGN_DATABASE.en).map((item) => (
            <button
              key={item.gesture}
              onClick={() => handleSimulateGesture(item.gesture, item.translation, item.confidence)}
              className="px-2 py-1.5 rounded-lg bg-white border border-slate-200/80 text-slate-700 hover:border-blue-300 hover:text-blue-600 active:scale-95 transition text-[10px] font-extrabold cursor-pointer flex items-center space-x-1"
            >
              <Sparkles className="w-3 h-3 text-indigo-500 shrink-0" />
              <span>{item.gesture}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TranslationBox;