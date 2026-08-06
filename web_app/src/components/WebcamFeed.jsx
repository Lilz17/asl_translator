import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from '../context/TranslationContext';
import { predictGesture } from '../services/api';
import { Video, AlertCircle } from 'lucide-react';

const CONNECTIONS = [
  [0,1],[1,2],[2,3],[3,4],
  [0,5],[5,6],[6,7],[7,8],
  [0,9],[9,10],[10,11],[11,12],
  [0,13],[13,14],[14,15],[15,16],
  [0,17],[17,18],[18,19],[19,20],
  [5,9],[9,13],[13,17]
];

const WebcamFeed = () => {
  const {
    cameraStatus,
    startCamera,
    stopCamera,
    isScanning,
    setIsScanning,
    selectedLanguage,
    setDetectedSign,
    setDetectedText,
    setConfidence,
    setLastDetectedTime,
  } = useTranslation();

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const pollRef = useRef(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const drawLandmarks = (landmarks) => {
    const canvas = canvasRef.current;
    if (!canvas || !landmarks || landmarks.length === 0) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const W = canvas.width;
    const H = canvas.height;
    const toX = (x) => (1 - x) * W;
    const toY = (y) => y * H;

    ctx.lineWidth = 3;
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.85)';
    ctx.shadowColor = 'rgba(59, 130, 246, 0.8)';
    ctx.shadowBlur = 10;

    CONNECTIONS.forEach(([start, end]) => {
      if (landmarks[start] && landmarks[end]) {
        ctx.beginPath();
        ctx.moveTo(toX(landmarks[start].x), toY(landmarks[start].y));
        ctx.lineTo(toX(landmarks[end].x), toY(landmarks[end].y));
        ctx.stroke();
      }
    });

    ctx.shadowBlur = 15;
    landmarks.forEach((pt, index) => {
      ctx.beginPath();
      if ([4, 8, 12, 16, 20].includes(index)) {
        ctx.fillStyle = '#f59e0b';
        ctx.shadowColor = '#f59e0b';
        ctx.arc(toX(pt.x), toY(pt.y), 6, 0, 2 * Math.PI);
      } else {
        ctx.fillStyle = '#10b981';
        ctx.shadowColor = '#10b981';
        ctx.arc(toX(pt.x), toY(pt.y), 4, 0, 2 * Math.PI);
      }
      ctx.fill();
    });
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
  };

  // Backend polling
  useEffect(() => {
    if (cameraStatus === 'active' && isScanning) {
      pollRef.current = setInterval(async () => {
        try {
          const video = videoRef.current;
          if (!video || video.readyState < 2) return;

          const snap = document.createElement('canvas');
          snap.width = video.videoWidth || 640;
          snap.height = video.videoHeight || 480;
          snap.getContext('2d').drawImage(video, 0, 0);
          const base64 = snap.toDataURL('image/jpeg', 0.7);

          console.log('Sending frame to backend...');
          const data = await predictGesture(base64);
          console.log('Backend response:', data);

          if (data.landmarks && data.landmarks.length > 0) {
            drawLandmarks(data.landmarks);
          } else {
            clearCanvas();
          }

          if (data.gesture) {
            setDetectedSign(data.gesture);
            setDetectedText(data.gesture);
            setConfidence(data.confidence);
            setLastDetectedTime(
              new Date().toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
              })
            );
          }
        } catch (err) {
          console.error('Prediction poll error:', err);
        }
      }, 500);
    } else {
      clearInterval(pollRef.current);
      clearCanvas();
    }

    return () => clearInterval(pollRef.current);
  }, [cameraStatus, isScanning]);

  // Camera stream
  useEffect(() => {
    if (cameraStatus === 'active') {
      setErrorMsg(null);
      navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720, facingMode: 'user' }
      })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
        }
      })
      .catch((err) => {
        console.error('Camera error:', err);
        setErrorMsg(
          selectedLanguage === 'hi'
            ? 'कैमरा इनपुट अनुपलब्ध है।'
            : 'Webcam not connected or permission denied.'
        );
      });
    } else {
      stopStreams();
    }

    return () => stopStreams();
  }, [cameraStatus]);

  const stopStreams = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    clearCanvas();
  };

  return (
    <div className="w-full relative overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-xs aspect-[16/10] sm:aspect-[16/9.5] flex flex-col justify-between group">

      {/* Floating Header */}
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

      {/* Main Stream */}
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
                  : 'Grant camera access to start real-time ASL translation.'}
              </p>
            </div>
            <button
              onClick={startCamera}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm px-7 py-3.5 rounded-2xl shadow-md active:scale-[0.98] transition cursor-pointer flex items-center justify-center mx-auto"
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
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover transform -scale-x-100"
            />
            <canvas
              ref={canvasRef}
              width={1280}
              height={720}
              className="absolute inset-0 w-full h-full object-cover pointer-events-none z-10"
            />
            <div className="absolute bottom-4 right-4 z-20 pointer-events-auto">
              <button
                onClick={stopCamera}
                className="bg-slate-900 hover:bg-slate-950 text-white font-bold text-xs px-4 py-2.5 rounded-xl transition cursor-pointer shadow-sm"
              >
                {selectedLanguage === 'hi' ? 'फीड बंद करें' : 'Turn Off Camera'}
              </button>
            </div>
          </>
        )}
      </div>

      {errorMsg && (
        <div className="absolute bottom-4 left-4 right-4 bg-amber-50/95 backdrop-blur-sm border border-amber-100 rounded-xl px-4 py-3 flex items-start space-x-2 text-amber-800 text-xs z-20 shadow-sm">
          <AlertCircle className="w-4 h-4 mr-1 text-amber-500 shrink-0 mt-0.5" />
          <span className="font-semibold">{errorMsg}</span>
        </div>
      )}
    </div>
  );
};

export default WebcamFeed;