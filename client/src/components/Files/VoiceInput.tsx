import React, { useState, useEffect, useRef } from "react";

interface AudioDevice {
  deviceId: string;
  label: string;
}

interface VoiceInputProps {
  onAudioRecorded?: (audioBlob: Blob, audioUrl: string) => void;
  className?: string;
  disabled?: boolean;
}

export const VoiceInput: React.FC<VoiceInputProps> = ({
  onAudioRecorded,
  className = "",
  disabled = false,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioDevices, setAudioDevices] = useState<AudioDevice[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>("");
  const [recordedAudio, setRecordedAudio] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingIntervalRef = useRef<number | null>(null);

  // Get supported MIME types for Safari compatibility
  const getSupportedMimeType = () => {
    const types = [
      "audio/webm;codecs=opus",
      "audio/webm;codecs=pcm",
      "audio/webm",
      "audio/mp4",
      "audio/ogg;codecs=opus",
      "audio/wav",
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }

    // Fallback for Safari - it supports basic webm without codec specification
    return "audio/webm";
  };

  // Get available audio devices
  useEffect(() => {
    const getAudioDevices = async () => {
      try {
        // Request permission to access microphone
        await navigator.mediaDevices.getUserMedia({ audio: true });

        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputDevices = devices
          .filter((device) => device.kind === "audioinput")
          .map((device) => ({
            deviceId: device.deviceId,
            label: device.label || `Microphone ${device.deviceId.slice(0, 8)}`,
          }));

        setAudioDevices(audioInputDevices);
        if (audioInputDevices.length > 0) {
          setSelectedDevice(audioInputDevices[0].deviceId);
        }
      } catch (err) {
        setError("No se pudo acceder al micrófono. Verifica los permisos.");
        console.error("Error accessing microphone:", err);
      }
    };

    getAudioDevices();
  }, []);

  // Listen for device changes
  useEffect(() => {
    const handleDeviceChange = async () => {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputDevices = devices
        .filter((device) => device.kind === "audioinput")
        .map((device) => ({
          deviceId: device.deviceId,
          label: device.label || `Microphone ${device.deviceId.slice(0, 8)}`,
        }));

      setAudioDevices(audioInputDevices);
    };

    navigator.mediaDevices.addEventListener("devicechange", handleDeviceChange);
    return () => {
      navigator.mediaDevices.removeEventListener(
        "devicechange",
        handleDeviceChange
      );
    };
  }, []);

  const startRecording = async () => {
    try {
      setError(null);
      audioChunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          deviceId: selectedDevice ? { exact: selectedDevice } : undefined,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      const mimeType = getSupportedMimeType();
      let mediaRecorder: MediaRecorder;

      try {
        mediaRecorder = new MediaRecorder(stream, { mimeType });
      } catch (err) {
        // Fallback: create MediaRecorder without specifying mimeType for Safari
        console.warn(
          "Failed to create MediaRecorder with specified mimeType, using default:",
          err
        );
        mediaRecorder = new MediaRecorder(stream);
      }

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        // Determine the correct blob type based on what was actually recorded
        const actualMimeType =
          mediaRecorder.mimeType || mimeType || "audio/webm";
        const audioBlob = new Blob(audioChunksRef.current, {
          type: actualMimeType,
        });

        const audioUrl = URL.createObjectURL(audioBlob);
        setRecordedAudio(audioUrl);

        if (onAudioRecorded) {
          onAudioRecorded(audioBlob, audioUrl);
        }

        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());
      };

      // Safari requires a timeslice for ondataavailable to fire
      mediaRecorder.start(1000);
      setIsRecording(true);
      setRecordingTime(0);

      // Start recording timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      setError(
        "Error al iniciar la grabación. Verifica los permisos del micrófono."
      );
      console.error("Error starting recording:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
    }
  };

  // const clearRecording = () => {
  //   if (recordedAudio) {
  //     URL.revokeObjectURL(recordedAudio);
  //     setRecordedAudio(null);
  //   }
  // };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  useEffect(() => {
    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
      if (recordedAudio) {
        URL.revokeObjectURL(recordedAudio);
      }
    };
  }, [recordedAudio]);

  return (
    <div className={`voice-input ${className}`}>
      {error && (
        <div
          className="error-message"
          style={{ color: "red", marginBottom: "10px" }}
        >
          {error}
        </div>
      )}

      {/* Recording Controls */}
      <div style={{ marginBottom: "15px" }}>
        {!isRecording ? (
          <button
            className="border border-gray-300 rounded-full px-4 py-2 hover:bg-gray-100 cursor-pointer"
            type="button"
            onClick={startRecording}
            disabled={disabled || audioDevices.length === 0}
          >
            🎤 Grabar
          </button>
        ) : (
          <button
            type="button"
            onClick={stopRecording}
            style={{
              backgroundColor: "#dc3545",
              color: "white",
              border: "none",
              padding: "10px 20px",
              borderRadius: "100px",
              cursor: "pointer",
            }}
          >
            ⏹️ Detener Grabación ({formatTime(recordingTime)})
          </button>
        )}
      </div>

      {/* Recording Indicator */}
      {isRecording && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            marginBottom: "15px",
            color: "#dc3545",
          }}
        >
          <div
            style={{
              width: "12px",
              height: "12px",
              borderRadius: "50%",
              backgroundColor: "#dc3545",
              marginRight: "8px",
              animation: "pulse 1s infinite",
            }}
          />
          Grabando... {formatTime(recordingTime)}
        </div>
      )}

      <style>{`
        @keyframes pulse {
          0% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
          100% {
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};
