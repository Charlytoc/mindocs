import { createWorkflow } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import { Modal } from "../Modal/Modal";
import { useState } from "react";
import { FileInput } from "../Files/FileInput";
import toast from "react-hot-toast";

export const WorkflowForm = () => {
  const { user } = useAuthStore();
  const [isOpen, setIsOpen] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [descriptions, setDescriptions] = useState<string[]>([]);

  const handleFileChange = (newFiles: FileList | null) => {
    if (!newFiles) return;

    const fileArray = Array.from(newFiles);
    setFiles((prev) => {
      const newFiles = [...prev, ...fileArray];
      return newFiles;
    });

    // Initialize descriptions array
    const newDescriptions = fileArray.map(() => "");
    setDescriptions((prev) => [...prev, ...newDescriptions]);
  };

  const handleDescriptionChange = (index: number, value: string) => {
    const newDescriptions = [...descriptions];
    newDescriptions[index] = value;
    setDescriptions(newDescriptions);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
    setDescriptions((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    
    e.preventDefault();
    if (!user) {
      toast.error("Debes estar autenticado para continuar");
      return;
    }

    const formData = new FormData(e.target as HTMLFormElement);
    const name = formData.get("name") as string;
    const description = formData.get("description") as string;
    const instructions = formData.get("instructions") as string;

    if (!name || !description || !instructions) {
      toast.error("Todos los campos son obligatorios");
      return;
    }

    try {
      const response = await createWorkflow(
        name,
        description,
        instructions,
        files,
        descriptions,
        user.email
      );

      toast.success("Workflow creado exitosamente");
      console.log(response);
      setIsOpen(false);

      // Reset form
      setFiles([]);
      setDescriptions([]);
    } catch (error) {
      console.error(error);
      toast.error("Error al crear el workflow");
    }
  };

  const handleClear = () => {
    setFiles([]);
    setDescriptions([]);
  };

  return (
    <>
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <button
          className="bg-blue-500 text-white rounded-md p-2"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? "Cerrar" : "Crear nuevo flujo de trabajo"}
        </button>
      </div>
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <div className="flex flex-col gap-4 p-4">
          <h2 className="text-2xl font-bold">Crear flujo de trabajo</h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-2">
            <input
              className="w-full border-2 border-gray-300 rounded-md p-2"
              type="text"
              name="name"
              placeholder="Nombre del flujo de trabajo"
              required
            />
            <div className="flex flex-col gap-2">
              <label htmlFor="description">Descripción</label>
              <textarea
                className="w-full border-2 border-gray-300 rounded-md p-2"
                name="description"
                placeholder="Descripción del flujo de trabajo"
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="instructions">Instrucciones</label>
              <textarea
                className="w-full border-2 border-gray-300 rounded-md p-2"
                name="instructions"
                placeholder="Instrucciones para el agente IA"
                required
              />
            </div>
            <div>
              <label htmlFor="output_examples">Archivos de ejemplo</label>
              <FileInput
                name="output_examples"
                label="Archivos de ejemplo"
                accept="image/*,.pdf,.doc,.docx,.txt,.csv,.mp3,.wav,.m4a,.webm,.weba"
                multiple={true}
                onChange={handleFileChange}
              />
            </div>

            {/* File descriptions */}
            {files.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800">
                  Descripciones de archivos de ejemplo
                </h3>
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="space-y-2 p-4 border border-gray-200 rounded-lg bg-gray-50"
                  >
                    <div className="flex justify-between items-center">
                      <label className="block text-sm font-medium text-gray-700">
                        📄 {file.name}
                      </label>
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        🗑️ Eliminar
                      </button>
                    </div>
                    <textarea
                      value={descriptions[index] || ""}
                      onChange={(e) =>
                        handleDescriptionChange(index, e.target.value)
                      }
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Descripción opcional del archivo de ejemplo..."
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
                Limpiar archivos
              </button>
              <button
                className="bg-blue-500 text-white rounded-md p-2"
                type="submit"
              >
                Create
              </button>
            </div>
          </form>
        </div>
      </Modal>
    </>
  );
};
