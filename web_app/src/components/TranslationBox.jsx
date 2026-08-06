import React from 'react';
import { useTranslation } from '../context/TranslationContext';
import { predictGesture } from '../services/api';
import {
  Volume2,
  Bookmark,
  Check,
  Sparkles,
  Terminal
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const TranslationBox = () => {
  console.log("TranslationBox Loaded");

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

  const handleSpeak = () => {
    speakText(detectedText);
  };

  const handleSave = () => {
    if (!detectedText) return;

    saveCurrentTranslation();
    setSavedSuccess(true);

    setTimeout(() => {
      setSavedSuccess(false);
    }, 2000);
  };

  // Existing simulator
  const handleSimulateGesture = (
    gesture,
    translation,
    conf
  ) => {
    setIsProcessing(true);

    setTimeout(() => {
      setDetectedSign(gesture);
      setDetectedText(translation);
      setConfidence(conf);
      setIsProcessing(false);
    }, 650);
  };

  // NEW FASTAPI CALL
  const handleBackendPrediction =
  async () => {
    try {

        console.log(
          "BUTTON CLICKED"
        );

      setIsProcessing(true);

      const data =
        await predictGesture();

      console.log(data);

      setDetectedSign(
        data.gesture
      );

      setDetectedText(
        data.gesture
      );

      setConfidence(
        data.confidence
      );

      setIsProcessing(false);
    } catch (err) {
      console.log(err);
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-4">

      {/* Existing Translation Box */}
      {/* Keep all your existing UI unchanged */}

      {/* Emulator Section */}
      <div className="p-6 bg-white rounded-2xl border">
  <h3 className="font-bold">
    Detected Sign:
  </h3>

  <p>{detectedSign || "None"}</p>

  <h3 className="font-bold mt-4">
    Translation:
  </h3>

  <p>{detectedText || "None"}</p>

  <h3 className="font-bold mt-4">
    Confidence:
  </h3>

  <p>{confidence || 0}%</p>
</div>
      <div className="bg-slate-50/50 border border-slate-100 rounded-3xl p-4">

        <div className="flex items-center space-x-1.5 border-b border-slate-100 pb-2 mb-2.5">
          <Terminal className="w-3.5 h-3.5 text-indigo-500" />

          <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">
            Vision Payload Emulator
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5 justify-center">

          {/* NEW TEST BUTTON */}
          <button
            onClick={handleBackendPrediction}
            className="px-3 py-2 rounded-lg bg-blue-600 text-white text-xs font-bold"
          >
            Test FastAPI
          </button>

          {(SIGN_DATABASE[selectedLanguage] ||
            SIGN_DATABASE.en).map((item) => (
            <button
              key={item.gesture}
              onClick={() =>
                handleSimulateGesture(
                  item.gesture,
                  item.translation,
                  item.confidence
                )
              }
              className="px-2 py-1.5 rounded-lg bg-white border border-slate-200/80 text-slate-600 hover:border-blue-300 hover:text-blue-600 active:scale-95 transition text-[10px] font-extrabold cursor-pointer flex items-center space-x-1"
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