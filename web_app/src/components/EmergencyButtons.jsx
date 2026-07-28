import React from 'react';
import { useTranslation } from '../context/TranslationContext';
import { ShieldAlert, Droplet, Stethoscope, PhoneCall, AlertOctagon } from 'lucide-react';
import { motion } from 'framer-motion';

const EmergencyButtons = () => {
  const { triggerEmergency, selectedLanguage } = useTranslation();

  const emergencyPhrases = [
    {
      id: 'help',
      labelEn: 'Help',
      labelHi: 'मदद',
      speakEn: 'I need urgent help!',
      speakHi: 'मुझे तुरंत मदद चाहिए!',
      icon: <PhoneCall className="w-3.5 h-3.5 mr-1.5 shrink-0" />,
      colorClass: 'bg-amber-50 hover:bg-amber-100 text-amber-700 border-amber-200/60 focus:ring-amber-300/40',
    },
    {
      id: 'doctor',
      labelEn: 'Doctor',
      labelHi: 'चिकित्सक',
      speakEn: 'I need medical assistance!',
      speakHi: 'मुझे चिकित्सा सहायता की आवश्यकता है!',
      icon: <Stethoscope className="w-3.5 h-3.5 mr-1.5 shrink-0" />,
      colorClass: 'bg-sky-50 hover:bg-sky-100 text-sky-700 border-sky-200/60 focus:ring-sky-300/40',
    },
    {
      id: 'water',
      labelEn: 'Water',
      labelHi: 'पानी',
      speakEn: 'I need water, please.',
      speakHi: 'मुझे पानी चाहिए, कृपया।',
      icon: <Droplet className="w-3.5 h-3.5 mr-1.5 shrink-0" />,
      colorClass: 'bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200/60 focus:ring-blue-300/40',
    },
    {
      id: 'emergency',
      labelEn: 'Emergency',
      labelHi: 'आपातकालीन',
      speakEn: 'Emergency! Please call for assistance immediately!',
      speakHi: 'आपातकाल! कृपया तुरंत सहायता बुलाएं!',
      icon: <AlertOctagon className="w-3.5 h-3.5 mr-1.5 shrink-0" />,
      colorClass: 'bg-rose-50 hover:bg-rose-100 text-rose-700 border-rose-200/60 focus:ring-rose-300/40 animate-pulse-slow font-black',
    },
  ];

  return (
    <div className="bg-white border border-slate-100 rounded-3xl p-5 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
      
      {/* Label and Badge */}
      <div className="flex items-center space-x-2 shrink-0">
        <ShieldAlert className="w-4.5 h-4.5 text-rose-500" />
        <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">
          {selectedLanguage === 'hi' ? 'त्वरित आपातकाल' : 'Quick Actions'}
        </span>
      </div>

      {/* Row of pills */}
      <div className="w-full flex flex-wrap sm:flex-nowrap gap-2 justify-center sm:justify-end">
        {emergencyPhrases.map((item) => (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            key={item.id}
            onClick={() => triggerEmergency(item.speakEn, item.speakHi)}
            className={`flex items-center justify-center px-4 py-2.5 rounded-full border text-xs font-extrabold shadow-2xs transition-all duration-200 cursor-pointer accessible-focus shrink-0 ${item.colorClass}`}
            aria-label={`Trigger emergency alarm: ${item.labelEn}`}
          >
            {item.icon}
            <span>{selectedLanguage === 'hi' ? item.labelHi : item.labelEn}</span>
          </motion.button>
        ))}
      </div>

    </div>
  );
};

export default EmergencyButtons;
