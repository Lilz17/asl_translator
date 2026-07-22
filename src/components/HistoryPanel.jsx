import React from 'react';
import { useTranslation } from '../context/TranslationContext';
import { Clock, Trash2, ShieldAlert, History } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const HistoryPanel = () => {
  const {
    history,
    deleteHistoryItem,
    clearHistory,
    selectedLanguage,
    speakText,
    exportTranscript
  } = useTranslation();

  return (
    <div className="bg-white border border-slate-100 rounded-3xl p-5 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
      {/* Header Label */}
      <div className="flex items-center space-x-2 shrink-0">
        <History className="w-4.5 h-4.5 text-blue-500" />
        <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">
          {selectedLanguage === 'hi' ? 'हालिया इतिहास' : 'Recent Translations'}
        </span>
      </div>

      {/* Dynamic horizontal stream */}
      <div className="flex-grow w-full overflow-x-auto scrollbar-none flex items-center gap-2 justify-center md:justify-start">
        <AnimatePresence mode="popLayout">
          {history.length === 0 ? (
            <span className="text-[11px] text-slate-400 font-semibold italic">
              {selectedLanguage === 'hi' ? 'इतिहास रिक्त है' : 'Logs are currently empty'}
            </span>
          ) : (
            <div className="flex items-center space-x-2 w-full overflow-x-auto py-1 scrollbar-none">
              {history.slice(0, 6).map((item, idx) => (
                <div key={item.id} className="flex items-center shrink-0">
                  {idx > 0 && <span className="text-slate-300 mx-2 text-xs font-black">•</span>}
                  
                  <motion.button
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    onClick={() => speakText(item.text)}
                    className={`px-3 py-1.5 rounded-full border text-[11px] font-extrabold flex items-center space-x-1.5 cursor-pointer accessible-focus transition-all ${
                      item.isEmergency 
                        ? 'bg-rose-50 hover:bg-rose-100 text-rose-700 border-rose-150' 
                        : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200/60'
                    }`}
                  >
                    {item.isEmergency && <ShieldAlert className="w-3 h-3 text-rose-500" />}
                    <span>{item.text}</span>
                  </motion.button>
                </div>
              ))}
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Actions */}
      {history.length > 0 && (
        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={exportTranscript}
            className="px-3.5 py-2.5 rounded-2xl bg-blue-50 hover:bg-blue-100 border border-blue-200/80 text-blue-600 hover:text-blue-700 text-xs font-bold transition cursor-pointer flex items-center space-x-1.5"
            title="Save Transcript"
          >
            <span>{selectedLanguage === 'hi' ? 'ट्रांसक्रिप्ट सहेजें' : 'Save Transcript'}</span>
          </button>
          
          <button
            onClick={clearHistory}
            className="p-3 rounded-2xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-400 hover:text-rose-500 transition cursor-pointer accessible-focus"
            title="Clear Log"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};

export default HistoryPanel;
