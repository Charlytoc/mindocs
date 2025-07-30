import { useState, useRef } from "react";
import { startWorkflow } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import { FileInput } from "../Files/FileInput";
import toast from "react-hot-toast";

interface Workflow {
  id: string;
  name: string;
  description: string;
}

interface WorkflowUploadProps {
  workflow: Workflow;
  onUploadSuccess: ({ execution_id }: { execution_id: string }) => void;
  onBack: () => void;
}

export const WorkflowUpload = ({
  workflow,
  onUploadSuccess,
  onBack,
}: WorkflowUploadProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const [descriptions, setDescriptions] = useState<string[]>([]);
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!user) {
      toast.error("Debes estar autenticado para continuar");
      return;
    }

    if (files.length === 0) {
      toast.error("Debes seleccionar al menos un archivo");
      return;
    }

    setIsLoading(true);

    try {
      const response = await startWorkflow(
        workflow.id,
        files,
        descriptions,
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
            accept="image/*,.pdf,.doc,.docx,.txt"
            multiple={true}
            name="files"
            onChange={handleFileChange}
            required
          />
        </div>

        {/* File descriptions */}
        {files.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">
              Descripciones de archivos
            </h3>
            {files.map((file, index) => (
              <div key={index} className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  {file.name}
                </label>
                <textarea
                  value={descriptions[index] || ""}
                  onChange={(e) =>
                    handleDescriptionChange(index, e.target.value)
                  }
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Descripción opcional del archivo..."
                  rows={2}
                />
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
            disabled={isLoading || files.length === 0}
            className="py-2 px-4 bg-blue-600 text-white font-semibold rounded-lg shadow-md cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
          >
            {isLoading ? "Enviando archivos..." : "Iniciar Workflow"}
          </button>
        </div>
      </form>
    </div>
  );
};
