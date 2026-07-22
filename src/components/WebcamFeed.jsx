import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from '../context/TranslationContext';
import { CameraOff, Sparkles, Video, Play, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const WebcamFeed = () => {
  const { 
    cameraStatus, 
    startCamera, 
    stopCamera, 
    isScanning, 
    setIsScanning,
    selectedLanguage 
  } = useTranslation();

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [useSimulation, setUseSimulation] = useState(false);

  useEffect(() => {
    if (cameraStatus === 'active') {
      setErrorMsg(null);
      
      if (useSimulation) {
        startLandmarkSimulation();
        return;
      }

      navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720, facingMode: 'user' } 
      })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
          startLandmarkSimulation();
        }
      })
      .catch((err) => {
        console.error('Camera availability or permissions block:', err);
        setErrorMsg(
          selectedLanguage === 'hi'
            ? 'कैमरा इनपुट अनुपलब्ध है। सिमुलेशन इनपुट सक्रिय किया गया।'
            : 'Webcam not connected. Activating high-fidelity simulated vision tracker.'
        );
        setUseSimulation(true);
        startLandmarkSimulation();
      });
    } else {
      stopStreams();
    }

    return () => stopStreams();
  }, [cameraStatus, useSimulation]);

  const stopStreams = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
  };

  const startLandmarkSimulation = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let frame = 0;

    const generateHandLandmarks = (centerX, centerY, scale, time) => {
      const joints = [];
      const wave = Math.sin(time * 0.05) * 5;
      const waveY = Math.cos(time * 0.04) * 8;
      
      const wrist = { x: centerX + wave, y: centerY + 100 + waveY };
      joints.push(wrist);

      const thumb = [];
      for (let i = 1; i <= 4; i++) {
        thumb.push({
          x: wrist.x - (i * 20 * scale) + Math.sin(time * 0.1 + i) * 3,
          y: wrist.y - (i * 18 * scale) + Math.cos(time * 0.08 + i) * 3
        });
      }
      joints.push(...thumb);

      const knuckles = [
        { x: wrist.x - 20 * scale, y: wrist.y - 70 * scale },
        { x: wrist.x - 2 * scale, y: wrist.y - 75 * scale },
        { x: wrist.x + 18 * scale, y: wrist.y - 72 * scale },
        { x: wrist.x + 36 * scale, y: wrist.y - 65 * scale }
      ];

      const fingers = [
        { base: knuckles[0], angleX: -0.15, len: 18 },
        { base: knuckles[1], angleX: -0.02, len: 20 },
        { base: knuckles[2], angleX: 0.1, len: 19 },
        { base: knuckles[3], angleX: 0.22, len: 16 }
      ];

      fingers.forEach((f, fIdx) => {
        joints.push(f.base);
        let prevX = f.base.x;
        let prevY = f.base.y;
        
        for (let seg = 1; seg <= 3; seg++) {
          const curl = Math.sin(time * 0.06 + fIdx * 1.5) * (seg * 4);
          const x = prevX + (Math.sin(f.angleX) * f.len * scale) + curl;
          const y = prevY - (Math.cos(f.angleX) * f.len * scale) - (seg * 3);
          joints.push({ x, y });
          prevX = x;
          prevY = y;
        }
      });

      return joints;
    };

    const connections = [
      [0, 1], [1, 2], [2, 3], [3, 4], // Thumb
      [0, 5], [5, 6], [6, 7], [7, 8], // Index
      [0, 9], [9, 10], [10, 11], [11, 12], // Middle
      [0, 13], [13, 14], [14, 15], [15, 16], // Ring
      [0, 17], [17, 18], [18, 19], [19, 20], // Pinky
      [5, 9], [9, 13], [13, 17] // Palm knuckles joins
    ];

    const animate = () => {
      if (!canvas) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      frame++;

      if (isScanning) {
        const cx = canvas.width / 2 + Math.sin(frame * 0.02) * 40;
        const cy = canvas.height / 2 + Math.cos(frame * 0.015) * 30;
        const scale = 1.6;
        
        const landmarks = generateHandLandmarks(cx, cy, scale, frame);

        ctx.lineWidth = 4;
        ctx.strokeStyle = 'rgba(59, 130, 246, 0.75)'; // Soft blue glow
        ctx.shadowColor = 'rgba(59, 130, 246, 0.8)';
        ctx.shadowBlur = 12;

        connections.forEach(([start, end]) => {
          if (landmarks[start] && landmarks[end]) {
            ctx.beginPath();
            ctx.moveTo(landmarks[start].x, landmarks[start].y);
            ctx.lineTo(landmarks[end].x, landmarks[end].y);
            ctx.stroke();
          }
        });

        ctx.shadowBlur = 15;
        landmarks.forEach((pt, index) => {
          ctx.beginPath();
          if ([4, 8, 12, 16, 20].includes(index)) {
            ctx.fillStyle = '#f59e0b'; // Soft yellow tips
            ctx.shadowColor = '#f59e0b';
            ctx.arc(pt.x, pt.y, 6.5, 0, 2 * Math.PI);
          } else {
            ctx.fillStyle = '#10b981'; // Green joint markers
            ctx.shadowColor = '#10b981';
            ctx.arc(pt.x, pt.y, 4.5, 0, 2 * Math.PI);
          }
          ctx.fill();
        });

        // Soft visual scan line
        ctx.shadowBlur = 0;
        const laserY = (Math.sin(frame * 0.035) + 1) * (canvas.height / 2);
        const grad = ctx.createLinearGradient(0, laserY - 10, 0, laserY + 10);
        grad.addColorStop(0, 'rgba(59, 130, 246, 0)');
        grad.addColorStop(0.5, 'rgba(59, 130, 246, 0.35)');
        grad.addColorStop(1, 'rgba(59, 130, 246, 0)');
        ctx.fillStyle = grad;
        ctx.fillRect(10, laserY - 10, canvas.width - 20, 20);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();
  };

  const handleToggleSimulation = () => {
    stopStreams();
    setUseSimulation(!useSimulation);
  };

  return (
    <div className="w-full relative overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-xs aspect-[16/10] sm:aspect-[16/9.5] flex flex-col justify-between group">
      
      {/* Floating Header Controls */}
      <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-none">
        <div className="bg-slate-900/80 backdrop-blur-md rounded-xl px-3 py-1.5 flex items-center space-x-2 text-white text-xs font-semibold shadow-sm">
          <span className={`w-2 h-2 rounded-full ${cameraStatus === 'active' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`} />
          <span className="uppercase tracking-widest font-black text-[9px]">
            {cameraStatus === 'active' 
              ? (isScanning ? 'Model Active' : 'Detection Paused') 
              : 'Webcam Inactive'}
          </span>
        </div>

        {cameraStatus === 'active' && (
          <div className="flex items-center space-x-2 pointer-events-auto">
            <button
              onClick={handleToggleSimulation}
              className="text-[10px] font-bold px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-200/80 text-slate-700 shadow-sm transition flex items-center cursor-pointer"
            >
              <Sparkles className="w-3 h-3 mr-1.5 text-indigo-500" />
              {useSimulation 
                ? (selectedLanguage === 'hi' ? 'कैमरा चुनें' : 'Use Live Camera') 
                : (selectedLanguage === 'hi' ? 'वर्चुअल कैमरा चालू' : 'Virtual Camera')}
            </button>
            
            <button
              onClick={() => setIsScanning(!isScanning)}
              className={`text-[10px] font-bold px-3 py-1.5 rounded-xl transition shadow-sm cursor-pointer border ${
                isScanning 
                  ? 'bg-blue-50 border-blue-200/80 text-blue-600' 
                  : 'bg-amber-50 border-amber-200/80 text-amber-600'
              }`}
            >
              {isScanning 
                ? (selectedLanguage === 'hi' ? 'डिटेक्शन रोकें' : 'Pause Detection') 
                : (selectedLanguage === 'hi' ? 'डिटेक्शन शुरू' : 'Start Detection')}
            </button>
          </div>
        )}
      </div>


      {/* Main Stream Area */}
      <div className="flex-grow bg-slate-50/50 relative flex items-center justify-center overflow-hidden">
        {cameraStatus === 'off' && (
          <div className="text-center p-6 max-w-sm z-10 space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-blue-50 flex items-center justify-center text-blue-500 shadow-xs border border-blue-100">
              <Video className="w-7 h-7" />
            </div>
            <div>
              <h3 className="text-slate-800 text-base font-extrabold tracking-tight">
                {selectedLanguage === 'hi' ? 'कैमरा फीड प्रारंभ करें' : 'Enable Translation Camera'}
              </h3>
              <p className="text-slate-400 text-xs mt-1 leading-relaxed">
                {selectedLanguage === 'hi'
                  ? 'हाथ के संकेतों का रीयल-टाइम अनुवाद शुरू करने के लिए अपना वेबकैम चालू करें।'
                  : 'Grant camera access to process sign language letters or utilize simulated neural landmarks.'}
              </p>
            </div>
            <button
              onClick={startCamera}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm px-7 py-3.5 rounded-2xl shadow-md hover:shadow-blue-500/10 active:scale-[0.98] transition cursor-pointer flex items-center justify-center mx-auto"
            >
              <Video className="w-4 h-4 mr-2" />
              {selectedLanguage === 'hi' ? 'कैमरा शुरू करें' : 'Activate Camera Feed'}
            </button>
          </div>
        )}

        {cameraStatus === 'loading' && (
          <div className="text-center p-6 z-10 space-y-3">
            <div className="w-10 h-10 border-3 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">
              Connecting vision streams...
            </p>
          </div>
        )}

        {cameraStatus === 'active' && (
          <>
            {/* Real Webcam Stream */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`w-full h-full object-cover transform -scale-x-100 ${
                useSimulation ? 'hidden' : 'block'
              }`}
            />

            {/* Simulated Vision Backdrop */}
            {useSimulation && (
              <div className="absolute inset-0 bg-gradient-to-tr from-slate-100 via-white to-purple-50 flex items-center justify-center">
                <div className="absolute inset-0 bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] [background-size:24px_24px] opacity-30" />
                <div className="text-center z-10 pointer-events-none p-4 max-w-xs space-y-1">
                  <div className="w-10 h-10 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-500 mx-auto mb-2">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <h4 className="text-slate-800 text-xs font-bold uppercase tracking-wider">Virtual Camera Feed</h4>
                  <p className="text-slate-400 text-[10px]">Synthetic video stream mapping landmark tracking vectors</p>
                </div>
              </div>
            )}

            {/* Glowing Hand Skeleton Layer */}
            <canvas
              ref={canvasRef}
              width={1280}
              height={720}
              className="absolute inset-0 w-full h-full object-cover pointer-events-none z-10"
            />

            {/* Soft HUD controls absolute bottom */}
            <div className="absolute bottom-4 right-4 z-20 pointer-events-auto">
              <button
                onClick={stopCamera}
                className="bg-slate-900 hover:bg-slate-950 text-white font-bold text-xs px-4 py-2.5 rounded-xl transition cursor-pointer shadow-sm flex items-center"
              >
                {selectedLanguage === 'hi' ? 'फीड बंद करें' : 'Turn Off Camera'}
              </button>
            </div>
          </>
        )}
      </div>

      {/* Warning Toast Overlay */}
      {errorMsg && (
        <div className="absolute bottom-4 left-4 right-4 bg-amber-50/95 backdrop-blur-sm border border-amber-100 rounded-xl px-4 py-3 flex items-start space-x-2 text-amber-800 text-xs z-20 shadow-sm animate-fadeIn">
          <AlertCircle className="w-4 h-4 mr-1 text-amber-500 shrink-0 mt-0.5" />
          <span className="font-semibold">{errorMsg}</span>
        </div>
      )}
    </div>
  );
};

export default WebcamFeed;
