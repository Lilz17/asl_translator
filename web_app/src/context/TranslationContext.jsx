import React, { createContext, useContext, useState, useEffect } from 'react';

const TranslationContext = createContext();

export const useTranslation = () => {
  const context = useContext(TranslationContext);
  if (!context) {
    throw new Error('useTranslation must be used within a TranslationProvider');
  }
  return context;
};

const SIGN_DATABASE = {
  en: [
    { gesture: 'HELLO', confidence: 98, translation: 'Hello' },
    { gesture: 'THANK YOU', confidence: 96, translation: 'Thank you' },
    { gesture: 'NEED WATER', confidence: 94, translation: 'Need water' },
    { gesture: 'HELP', confidence: 99, translation: 'Help' },
    { gesture: 'YES', confidence: 95, translation: 'Yes' },
    { gesture: 'NO', confidence: 93, translation: 'No' },
    { gesture: 'PLEASE', confidence: 97, translation: 'Please' },
    { gesture: 'GOODBYE', confidence: 92, translation: 'Goodbye' },
  ],
  hi: [
    { gesture: 'HELLO', confidence: 98, translation: 'नमस्ते' },
    { gesture: 'THANK YOU', confidence: 96, translation: 'धन्यवाद' },
    { gesture: 'NEED WATER', confidence: 94, translation: 'मुझे पानी चाहिए' },
    { gesture: 'HELP', confidence: 99, translation: 'मदद कीजिये' },
    { gesture: 'YES', confidence: 95, translation: 'हाँ' },
    { gesture: 'NO', confidence: 93, translation: 'नहीं' },
    { gesture: 'PLEASE', confidence: 97, translation: 'कृपया' },
    { gesture: 'GOODBYE', confidence: 92, translation: 'अलविदा' },
  ]
};

export const TranslationProvider = ({ children }) => {
  const [detectedText, setDetectedText] = useState('');
  const [detectedSign, setDetectedSign] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [voiceGender, setVoiceGender] = useState('female');
  const [cameraStatus, setCameraStatus] = useState('off');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSpeechEnabled, setIsSpeechEnabled] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastDetectedTime, setLastDetectedTime] = useState(null);

  const [history, setHistory] = useState([
    { id: '1', sign: 'HELLO', text: 'Hello', timestamp: '10:30 AM', confidence: 98, date: 'Today' },
    { id: '2', sign: 'THANK YOU', text: 'Thank you', timestamp: '10:31 AM', confidence: 96, date: 'Today' },
    { id: '3', sign: 'NEED WATER', text: 'Need water', timestamp: '10:35 AM', confidence: 94, date: 'Today' },
    { id: '4', sign: 'HELP', text: 'Help', timestamp: '10:36 AM', confidence: 99, date: 'Today' },
  ]);

  const speakText = (textToSpeak) => {
    if (!textToSpeak) return;
    if (!('speechSynthesis' in window)) {
      console.warn('Text-to-speech not supported in this browser.');
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.lang = selectedLanguage === 'hi' ? 'hi-IN' : 'en-US';
    const voices = window.speechSynthesis.getVoices();
    let selectedVoice = null;
    if (selectedLanguage === 'hi') {
      selectedVoice = voices.find(v => v.lang.includes('hi') || v.lang.includes('IN'));
    } else {
      if (voiceGender === 'female') {
        selectedVoice = voices.find(v => v.lang.includes('en') && (
          v.name.includes('Google US English') || v.name.includes('Zira') ||
          v.name.includes('Samantha') || v.name.includes('Hazel') || v.name.includes('Moira')
        ));
      } else {
        selectedVoice = voices.find(v => v.lang.includes('en') && (
          v.name.includes('Google UK English') || v.name.includes('David') ||
          v.name.includes('Rishi') || v.name.includes('Daniel')
        ));
      }
    }
    if (selectedVoice) utterance.voice = selectedVoice;
    window.speechSynthesis.speak(utterance);
  };

  // Auto-speak when new gesture detected
  useEffect(() => {
    if (isSpeechEnabled && detectedText && !isProcessing) {
      speakText(detectedText);
    }
  }, [detectedText, isSpeechEnabled, isProcessing]);

  // Dark mode sync
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  // ── Fake simulator removed — real predictions come from WebcamFeed.jsx ──

  const startCamera = async () => {
    setCameraStatus('loading');
    setTimeout(() => {
      setCameraStatus('active');
      setIsScanning(true);
    }, 1200);
  };

  const stopCamera = () => {
    setCameraStatus('off');
    setIsScanning(false);
    setDetectedText('');
    setDetectedSign('');
    setConfidence(0);
  };

  const saveCurrentTranslation = () => {
    if (!detectedText) return;
    if (history.length > 0 && history[0].text === detectedText) return;
    const newItem = {
      id: Date.now().toString(),
      sign: detectedSign || 'MANUAL',
      text: detectedText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      confidence: confidence || 100,
      date: 'Today'
    };
    setHistory(prev => [newItem, ...prev]);
  };

  const clearOutput = () => {
    setDetectedText('');
    setDetectedSign('');
    setConfidence(0);
  };

  const deleteHistoryItem = (id) => {
    setHistory(prev => prev.filter(item => item.id !== id));
  };

  const clearHistory = () => {
    setHistory([]);
  };

  const triggerEmergency = (phraseEn, phraseHi) => {
    const text = selectedLanguage === 'hi' ? phraseHi : phraseEn;
    const sign = phraseEn.toUpperCase();

    setIsScanning(false); // pause webcam polling so it doesn't overwrite
    setDetectedSign(sign);
    setDetectedText(text);
    setConfidence(100);
    setLastDetectedTime(
      new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    );

    const newItem = {
      id: Date.now().toString(),
      sign: sign,
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      confidence: 100,
      date: 'Today',
      isEmergency: true
    };
    setHistory(prev => [newItem, ...prev]);
  };

  const exportTranscript = () => {
    if (history.length === 0) return;
    const title = `SignBridge Translation Transcript - ${new Date().toLocaleDateString()}\n==========================================\n\n`;
    const body = history
      .map(item => `[${item.timestamp}] Sign: ${item.sign} -> Translation: "${item.text}" (${item.confidence}% confidence)`)
      .join('\n');
    const blob = new Blob([title + body], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `signbridge-transcript-${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <TranslationContext.Provider value={{
      detectedText,
      setDetectedText,
      detectedSign,
      setDetectedSign,
      confidence,
      setConfidence,
      selectedLanguage,
      setSelectedLanguage,
      voiceGender,
      setVoiceGender,
      cameraStatus,
      setCameraStatus,
      isDarkMode,
      setIsDarkMode,
      isSpeechEnabled,
      setIsSpeechEnabled,
      isScanning,
      setIsScanning,
      lastDetectedTime,
      setLastDetectedTime,
      history,
      setHistory,
      startCamera,
      stopCamera,
      saveCurrentTranslation,
      clearOutput,
      deleteHistoryItem,
      clearHistory,
      triggerEmergency,
      exportTranscript,
      speakText,
      SIGN_DATABASE,
      isProcessing,
      setIsProcessing
    }}>
      {children}
    </TranslationContext.Provider>
  );
};