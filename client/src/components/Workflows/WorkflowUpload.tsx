import { useState, useRef } from "react";
import { startWorkflow } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import { FileInput } from "../Files/FileInput";
import { VoiceInput } from "../Files/VoiceInput";
import toast from "react-hot-toast";

interface Workflow {
  id: string;
  name: string;
  description: string;
}

interface WorkflowUploadProps {
  workflow: Workflow;
  // fetchWorkflow: () => void;
  onUploadSuccess: ({ execution_id }: { execution_id: string }) => void;
}

export const WorkflowUpload = ({
  workflow,
  // fetchWorkflow,
  onUploadSuccess,
}: WorkflowUploadProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const [descriptions, setDescriptions] = useState<string[]>([]);
  const [audioRecordings, setAudioRecordings] = useState<
    { blob: Blob; name: string; description: string }[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const inputTextRef = useRef<HTMLTextAreaElement>(null);
  const { user } = useAuthStore();

  const handleFileChange = (newFiles: FileList | null) => {
    if (!newFiles) return;

    const fileArray = Array.from(newFiles);
    setFiles((prev) => {
      const newFiles = [...prev, ...fileArray];
      return newFiles;
    });

    // Initialize descriptions array
    const newDescriptions = fileArray.map(() => "");
    setDescriptions(newDescriptions);
  };

  const handleDescriptionChange = (index: number, value: string) => {
    const newDescriptions = [...descriptions];
    newDescriptions[index] = value;
    setDescriptions(newDescriptions);
  };

  const handleAudioRecorded = (audioBlob: Blob) => {
    // Generate a unique filename with timestamp and random hash
    const timestamp = Date.now();
    const randomHash = Math.random().toString(36).substring(2, 15);
    const fileName = `audio_recording_${timestamp}_${randomHash}.webm`;

    setAudioRecordings((prev) => [
      ...prev,
      {
        blob: audioBlob,
        name: fileName,
        description: "",
      },
    ]);
  };

  const handleAudioDescriptionChange = (index: number, value: string) => {
    setAudioRecordings((prev) => {
      const newRecordings = [...prev];
      newRecordings[index] = { ...newRecordings[index], description: value };
      return newRecordings;
    });
  };

  const removeAudioRecording = (index: number) => {
    setAudioRecordings((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!user) {
      toast.error("Debes estar autenticado para continuar");
      return;
    }

    if (files.length === 0 && audioRecordings.length === 0 && !inputTextRef.current?.value) {
      toast.error("Debes seleccionar al menos un archivo, grabar audio o escribir un texto complementario");
      return;
    }

    setIsLoading(true);

    try {
      // Convert audio recordings to files and combine with regular files
      const allFiles = [...files];
      const allDescriptions = [...descriptions];

      // Add audio recordings as files
      audioRecordings.forEach((recording) => {
        const audioFile = new File([recording.blob], recording.name, {
          type: "audio/webm",
        });
        allFiles.push(audioFile);
        allDescriptions.push(recording.description);
      });

      const response = await startWorkflow(
        workflow.id,
        allFiles,
        allDescriptions,
        user.email,
        inputTextRef.current?.value
      );

      toast.success(
        "Archivos enviados, nuestro agente IA está trabajando en ello"
      );
      onUploadSuccess({ execution_id: response.workflow_execution_id });
    } catch (error) {
      console.error("Error al enviar archivos:", error);
      toast.error("Error al enviar los archivos");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setFiles([]);
    setDescriptions([]);
    setAudioRecordings([]);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      {/* Upload Form */}
      <h2 className="text-xl font-bold text-gray-800 mb-4">
        Ejecuta este flujo
      </h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Texto complementario
          </label>
          <textarea
            className="w-full border-2 border-gray-300 rounded-md p-2"
            name="input_text"
            placeholder="Texto complementario, información adicional, etc."
            ref={inputTextRef}
          />

          <label className="block text-sm font-medium text-gray-700 mb-2">
            Archivos
          </label>
          <FileInput
            label="Seleccionar archivos"
            accept="image/*,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,text/csv,audio/mpeg,audio/wav,audio/mp4,audio/webm,audio/weba"
            multiple={true}
            name="files"
            onChange={handleFileChange}
          />
        </div>

        {/* Audio Recording Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Grabación de Audio (Opcional)
          </label>
          <VoiceInput onAudioRecorded={handleAudioRecorded} />
        </div>

        {/* File descriptions */}
        {files.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">
              Descripciones de archivos
            </h3>
            {files.map((file, index) => (
              <div
                key={index}
                className="space-y-2 p-4 border border-gray-200 rounded-lg bg-gray-50"
              >
                <label className="block text-sm font-medium text-gray-700">
                  {file.name}
                </label>

                {/* Audio player for audio files */}
                {file.type.startsWith("audio/") && (
                  <div className="mb-3">
                    <audio
                      controls
                      src={URL.createObjectURL(file)}
                      className="w-full"
                    />
                  </div>
                )}

                <textarea
                  value={descriptions[index] || ""}
                  onChange={(e) =>
                    handleDescriptionChange(index, e.target.value)
                  }
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Descripción opcional del archivo..."
                  rows={2}
                />
                <div className="flex justify-end items-center">
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="text-red-600 hover:text-red-800 text-sm bg-red-100 px-2 py-1 rounded-md cursor-pointer hover:bg-red-200"
                  >
                    🗑️ Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Audio Recordings */}
        {audioRecordings.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">
              Grabaciones de Audio
            </h3>
            {audioRecordings.map((recording, index) => (
              <div
                key={index}
                className="space-y-2 p-4 border border-gray-200 rounded-lg bg-gray-50"
              >
                <audio
                  controls
                  src={URL.createObjectURL(recording.blob)}
                  className="w-full"
                />
                <textarea
                  value={recording.description}
                  onChange={(e) =>
                    handleAudioDescriptionChange(index, e.target.value)
                  }
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Descripción opcional de la grabación..."
                  rows={2}
                />
                <div className="flex justify-end items-center">
                  <button
                    type="button"
                    onClick={() => removeAudioRecording(index)}
                    className="text-red-600 hover:text-red-800 text-sm bg-red-100 px-2 py-1 rounded-md cursor-pointer hover:bg-red-200"
                  >
                    🗑️ Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Action buttons */}
        <div className="flex justify-between pt-6">
          <button
            type="button"
            onClick={handleClear}
            className="py-2 px-4 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 transition-colors"
          >
            Limpiar
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="py-2 px-4 bg-blue-600 text-white font-semibold rounded-lg shadow-md cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
          >
            {isLoading ? "Enviando archivos..." : "Iniciar Workflow"}
          </button>
        </div>
      </form>
    </div>
  );
};
