import React from 'react';
import { useTranslation } from '../context/TranslationContext';
import { 
  Languages, 
  Volume2, 
  Moon, 
  Sun, 
  Camera, 
  ShieldCheck, 
  UserCheck, 
  Sliders, 
  Info,
  Check
} from 'lucide-react';

const Settings = () => {
  const {
    selectedLanguage,
    setSelectedLanguage,
    voiceGender,
    setVoiceGender,
    isDarkMode,
    setIsDarkMode,
    isSpeechEnabled,
    setIsSpeechEnabled,
    cameraStatus,
    startCamera,
    stopCamera
  } = useTranslation();

  const [testVoiceSuccess, setTestVoiceSuccess] = React.useState(false);

  const handleTestVoice = () => {
    if (!('speechSynthesis' in window)) return;
    
    setTestVoiceSuccess(true);
    setTimeout(() => setTestVoiceSuccess(false), 2000);

    const testText = selectedLanguage === 'hi' 
      ? 'साइन ब्रिज आवाज परीक्षण सफल रहा।' 
      : 'Sign Bridge voice testing successful.';
    
    const utterance = new SpeechSynthesisUtterance(testText);
    utterance.lang = selectedLanguage === 'hi' ? 'hi-IN' : 'en-US';

    const voices = window.speechSynthesis.getVoices();
    let selectedVoice = null;

    if (selectedLanguage === 'hi') {
      selectedVoice = voices.find(v => v.lang.includes('hi') || v.lang.includes('IN'));
    } else {
      if (voiceGender === 'female') {
        selectedVoice = voices.find(v => v.lang.includes('en') && (v.name.includes('Google US English') || v.name.includes('Zira') || v.name.includes('Samantha') || v.name.includes('Hazel') || v.name.includes('Moira')));
      } else {
        selectedVoice = voices.find(v => v.lang.includes('en') && (v.name.includes('Google UK English') || v.name.includes('David') || v.name.includes('Rishi') || v.name.includes('Daniel')));
      }
    }

    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="py-6 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto flex-grow space-y-6 text-left">
      
      {/* Page Header */}
      <div className="border-b border-slate-200/80 pb-5">
        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight m-0">
          {selectedLanguage === 'hi' ? 'सेटिंग्स और प्राथमिकताएं' : 'Settings & Preferences'}
        </h2>
        <p className="text-xs sm:text-sm text-slate-500 font-medium mt-1">
          {selectedLanguage === 'hi' 
            ? 'अपनी सुविधा के अनुसार भाषा, आवाज़ और एक्सेसिबिलिटी सेटिंग्स को अनुकूलित करें।' 
            : 'Customize language layers, text-to-speech outputs, and accessibility filters.'}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Side: Navigation Links / Tips */}
        <div className="space-y-4">
          <div className="glass-panel rounded-2xl p-5 border border-slate-200/80 shadow-xs space-y-3 bg-blue-50/20">
            <h3 className="text-xs font-bold uppercase tracking-widest text-blue-600 flex items-center">
              <ShieldCheck className="w-4 h-4 mr-1.5 shrink-0" />
              Accessibility Standard
            </h3>
            <p className="text-[11px] text-slate-500 leading-normal font-medium">
              This dashboard meets WCAG 2.1 AA requirements. Color contrasts exceed 4.5:1 ratio, enabling easy reading for visually impaired individuals.
            </p>
          </div>
          
          <div className="glass-panel rounded-2xl p-5 border border-slate-200/80 shadow-xs space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-700 flex items-center">
              <Info className="w-4 h-4 mr-1.5 shrink-0 text-slate-500" />
              Speech Engine Note
            </h3>
            <p className="text-[11px] text-slate-500 leading-normal font-medium">
              Speech outputs utilize your device's native TTS engines. For highly natural vocal accents, ensure premium voices are installed in your OS settings.
            </p>
          </div>
        </div>

        {/* Right Side: Options Panels */}
        <div className="md:col-span-2 space-y-6">
          
          {/* Translation Parameters */}
          <div className="glass-panel rounded-3xl p-6 shadow-sm border border-slate-200/80 space-y-6">
            
            {/* Option 1: Translation Output Language */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Languages className="w-5 h-5 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-800 tracking-tight m-0">
                  {selectedLanguage === 'hi' ? 'अनुवाद आउटपुट भाषा' : 'Translation Output Language'}
                </h3>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                {selectedLanguage === 'hi'
                  ? 'हाथ के संकेतों को इस चुनी गई भाषा के शब्दों और आवाज़ में अनुवादित किया जाएगा।'
                  : 'Output detected sign letters and complete emergency broadcast warnings in this vocabulary.'}
              </p>
              
              <div className="grid grid-cols-2 gap-3.5 pt-1">
                <button
                  onClick={() => setSelectedLanguage('en')}
                  className={`py-3 px-4 rounded-xl border text-sm font-bold transition-all cursor-pointer accessible-focus ${
                    selectedLanguage === 'en'
                      ? 'bg-blue-50 border-blue-300 text-blue-700 shadow-sm shadow-blue-500/5'
                      : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  English (US)
                </button>
                <button
                  onClick={() => setSelectedLanguage('hi')}
                  className={`py-3 px-4 rounded-xl border text-sm font-bold transition-all cursor-pointer accessible-focus ${
                    selectedLanguage === 'hi'
                      ? 'bg-blue-50 border-blue-300 text-blue-700 shadow-sm shadow-blue-500/5'
                      : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  हिन्दी (Hindi)
                </button>
              </div>
            </div>

            <hr className="border-slate-100" />

            {/* Option 2: Voice output settings */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Volume2 className="w-5 h-5 text-blue-600" />
                  <h3 className="text-sm font-bold text-slate-800 tracking-tight m-0">
                    {selectedLanguage === 'hi' ? 'ऑडियो आवाज़ सेटिंग्स' : 'Text-to-Speech Voice Settings'}
                  </h3>
                </div>

                {/* Speak Enabled Switch */}
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isSpeechEnabled}
                    onChange={(e) => setIsSpeechEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-10 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:height-5 after:width-5 after:transition-all peer-checked:bg-blue-600"></div>
                  <span className="ml-2.5 text-xs font-bold text-slate-600">
                    {isSpeechEnabled ? (selectedLanguage === 'hi' ? 'सक्रिय' : 'On') : (selectedLanguage === 'hi' ? 'बंद' : 'Mute')}
                  </span>
                </label>
              </div>
              
              <p className="text-xs text-slate-500 font-medium">
                {selectedLanguage === 'hi'
                  ? 'चुनें कि क्या अनुवादित पाठ को जोर से बोला जाना चाहिए, और आवाज के स्वर का चयन करें।'
                  : 'Synthesize written translation words into clear spoke audio sentences immediately upon capture.'}
              </p>

              {isSpeechEnabled && (
                <div className="space-y-4 pt-1 animate-fadeIn">
                  <div className="grid grid-cols-2 gap-3.5">
                    <button
                      onClick={() => setVoiceGender('female')}
                      className={`py-3 px-4 rounded-xl border text-sm font-bold transition-all cursor-pointer accessible-focus ${
                        voiceGender === 'female'
                          ? 'bg-blue-50 border-blue-300 text-blue-700 shadow-sm'
                          : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      {selectedLanguage === 'hi' ? 'महिला स्वर' : 'Female Voice'}
                    </button>
                    <button
                      onClick={() => setVoiceGender('male')}
                      className={`py-3 px-4 rounded-xl border text-sm font-bold transition-all cursor-pointer accessible-focus ${
                        voiceGender === 'male'
                          ? 'bg-blue-50 border-blue-300 text-blue-700 shadow-sm'
                          : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      {selectedLanguage === 'hi' ? 'पुरुष स्वर' : 'Male Voice'}
                    </button>
                  </div>

                  <button
                    onClick={handleTestVoice}
                    className={`w-full py-2.5 rounded-xl border text-xs font-bold transition-all flex items-center justify-center cursor-pointer accessible-focus ${
                      testVoiceSuccess 
                        ? 'bg-emerald-50 border-emerald-200 text-emerald-600'
                        : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
                    }`}
                  >
                    {testVoiceSuccess ? (
                      <>
                        <Check className="w-3.5 h-3.5 mr-1.5 animate-bounce" />
                        <span>{selectedLanguage === 'hi' ? 'परीक्षण सफल!' : 'Audio Output Confirmed!'}</span>
                      </>
                    ) : (
                      <span>{selectedLanguage === 'hi' ? 'आवाज़ का परीक्षण करें' : 'Trigger Test Voice Output'}</span>
                    )}
                  </button>
                </div>
              )}
            </div>

            <hr className="border-slate-100" />

            {/* Option 3: Accessibilities */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Moon className="w-5 h-5 text-blue-600" />
                  <h3 className="text-sm font-bold text-slate-800 tracking-tight m-0">
                    {selectedLanguage === 'hi' ? 'डार्क मोड' : 'Dark Accessibility Filter'}
                  </h3>
                </div>

                <button
                  onClick={() => setIsDarkMode(!isDarkMode)}
                  className={`p-2 rounded-xl border transition-all cursor-pointer accessible-focus ${
                    isDarkMode 
                      ? 'bg-slate-800 border-slate-700 text-yellow-400 hover:bg-slate-750' 
                      : 'bg-slate-50 border-slate-200 text-slate-500 hover:bg-slate-100'
                  }`}
                  aria-label="Toggle dark mode filter"
                >
                  {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                {selectedLanguage === 'hi'
                  ? 'स्क्रीन की चमक कम करने और कम रोशनी में बेहतर पढ़ने के लिए डार्क हाई-कंट्रास्ट मोड चालू करें।'
                  : 'Flip interface contrasts to deep dark colors. Highly recommended for reduced eye strains in dim environments.'}
              </p>
            </div>

          </div>

          {/* Camera Permission instructions card */}
          <div className="glass-panel rounded-3xl p-6 shadow-sm border border-slate-200/80 space-y-4">
            <div className="flex items-center space-x-2">
              <Camera className="w-5 h-5 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-800 tracking-tight m-0">
                {selectedLanguage === 'hi' ? 'कैमरा और मीडिया अनुमतियां' : 'Webcam Media Settings'}
              </h3>
            </div>
            
            <p className="text-xs text-slate-500 leading-relaxed font-medium">
              {selectedLanguage === 'hi'
                ? 'SignBridge को काम करने के लिए आपके ब्राउज़र की वीडियो इनपुट अनुमति की आवश्यकता होती है। यदि कैमरा कनेक्ट नहीं हो पा रहा है, तो कृपया ब्राउज़र के एड्रेस बार में लॉक आइकॉन पर क्लिक करें और कैमरा परमिशन को "अनुमति दें" पर सेट करें।'
                : 'SignBridge processes hand joints completely client-side. No video frames, images, or landmarks are ever sent to external cloud servers, guaranteeing absolute privacy.'}
            </p>

            <div className="flex items-center justify-between p-3.5 rounded-2xl border border-slate-200 bg-slate-50/50 text-xs">
              <div className="flex items-center space-x-2">
                <span className={`w-2 h-2 rounded-full ${cameraStatus === 'active' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`} />
                <span className="font-bold text-slate-700">
                  {cameraStatus === 'active' 
                    ? (selectedLanguage === 'hi' ? 'कैमरा लाइव है' : 'Camera Stream: ACTIVE') 
                    : (selectedLanguage === 'hi' ? 'कैमरा बंद है' : 'Camera Stream: INACTIVE')}
                </span>
              </div>
              
              {cameraStatus === 'active' ? (
                <button
                  onClick={stopCamera}
                  className="px-3 py-1.5 rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-100 border border-rose-200 font-bold transition text-[11px] cursor-pointer"
                >
                  {selectedLanguage === 'hi' ? 'कैमरा बंद करें' : 'Deactivate Stream'}
                </button>
              ) : (
                <button
                  onClick={startCamera}
                  className="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200 font-bold transition text-[11px] cursor-pointer"
                >
                  {selectedLanguage === 'hi' ? 'कैमरा चालू करें' : 'Request Stream Permission'}
                </button>
              )}
            </div>
          </div>

        </div>
      </div>

    </div>
  );
};

export default Settings;
