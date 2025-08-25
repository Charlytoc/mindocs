import { createWorkflow } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import { Modal } from "../Modal/Modal";
import { useState } from "react";
import { FileInput } from "../Files/FileInput";
import toast from "react-hot-toast";

export const WorkflowForm = () => {
  const { user } = useAuthStore();
  const [isOpen, setIsOpen] = useState(false);
  
  // Separate state for template and examples
  const [templateDocx, setTemplateDocx] = useState<File | null>(null);
  const [examples, setExamples] = useState<File[]>([]);
  const [exampleDescriptions, setExampleDescriptions] = useState<string[]>([]);

  const handleTemplateChange = (newFiles: FileList | null) => {
    if (!newFiles || newFiles.length === 0) return;
    
    // Only take the first file since we only allow one template
    const file = newFiles[0];
    
    // Validate it's a .docx file
    if (!file.name.endsWith('.docx')) {
      toast.error("La plantilla debe ser un archivo .docx");
      return;
    }
    
    setTemplateDocx(file);
  };

  const handleExampleChange = (newFiles: FileList | null) => {
    if (!newFiles) return;

    const fileArray = Array.from(newFiles);
    setExamples((prev: File[]) => {
      const newExamples = [...prev, ...fileArray];
      return newExamples;
    });

    // Initialize example descriptions array
    const newDescriptions = fileArray.map(() => "");
    setExampleDescriptions((prev: string[]) => [...prev, ...newDescriptions]);
  };



  const handleExampleDescriptionChange = (index: number, value: string) => {
    const newDescriptions = [...exampleDescriptions];
    newDescriptions[index] = value;
    setExampleDescriptions(newDescriptions);
  };

  const removeTemplate = () => {
    setTemplateDocx(null);
  };

  const removeExample = (index: number) => {
    setExamples((prev) => prev.filter((_, i) => i !== index));
    setExampleDescriptions((prev) => prev.filter((_, i) => i !== index));
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
        templateDocx,
        examples,
        exampleDescriptions,
        user.email
      );

      toast.success("Workflow creado exitosamente");
      console.log(response);
      setIsOpen(false);

      // Reset form
      setTemplateDocx(null);
      setExamples([]);
      setExampleDescriptions([]);
    } catch (error) {
      console.error(error);
      toast.error("Error al crear el workflow");
    }
  };

  const handleClear = () => {
    setTemplateDocx(null);
    setExamples([]);
    setExampleDescriptions([]);
  };

  return (
    <>
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-6 rounded-lg">
        <button
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors shadow-sm hover:shadow-md flex items-center space-x-2"
          onClick={() => setIsOpen(!isOpen)}
        >
          <span>{isOpen ? "✕" : "✨"}</span>
          <span>{isOpen ? "Cerrar" : "Crear nuevo flujo de trabajo"}</span>
        </button>
      </div>
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <div className="flex flex-col gap-6 p-6 max-w-2xl mx-auto">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-800 mb-2">Crear flujo de trabajo</h2>
            <p className="text-gray-600">Define un nuevo flujo de trabajo con plantillas y ejemplos</p>
          </div>
          <form onSubmit={handleSubmit} className="flex flex-col gap-6">
            <div className="space-y-2">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Nombre del flujo de trabajo *
              </label>
              <input
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                type="text"
                name="name"
                placeholder="Ej: Generación de contratos"
                required
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Descripción *
              </label>
              <textarea
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                name="description"
                placeholder="Describe el propósito del flujo de trabajo"
                rows={3}
                required
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="instructions" className="block text-sm font-medium text-gray-700">
                Instrucciones para la IA *
              </label>
              <textarea
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                name="instructions"
                placeholder="Instrucciones específicas para el agente IA"
                rows={4}
                required
              />
            </div>
            
            {/* Plantillas (Templates with placeholders) */}
            <div className="space-y-3 p-4 border border-blue-200 rounded-lg bg-blue-50">
              <div className="flex items-center space-x-2">
                <span className="text-blue-600 text-xl">📋</span>
                <label htmlFor="template_docx" className="text-sm font-semibold text-gray-800">
                  Plantilla (.docx con placeholders)
                </label>
              </div>
              <p className="text-sm text-gray-600 ml-6">
                Documento .docx que contiene placeholders como &#123;&#123; nombre &#125;&#125; que la IA rellenará
              </p>
              <div className="ml-6">
                <FileInput
                  name="template_docx"
                  label="Seleccionar plantilla"
                  accept=".docx"
                  multiple={false}
                  onChange={handleTemplateChange}
                />
              </div>
            </div>

            {/* Examples (Final document examples) */}
            <div className="space-y-3 p-4 border border-green-200 rounded-lg bg-green-50">
              <div className="flex items-center space-x-2">
                <span className="text-green-600 text-xl">📄</span>
                <label htmlFor="examples" className="text-sm font-semibold text-gray-800">
                  Ejemplos de referencia
                </label>
              </div>
              <p className="text-sm text-gray-600 ml-6">
                Archivos que muestran cómo debe verse el documento final generado
              </p>
              <div className="ml-6">
                <FileInput
                  name="examples"
                  label="Seleccionar ejemplos"
                  accept="image/*,.pdf,.docx,.txt,.csv,.mp3,.wav,.m4a,.webm,.weba"
                  multiple={true}
                  onChange={handleExampleChange}
                />
              </div>
            </div>

            {/* Template display */}
            {templateDocx && (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
                  <span className="text-blue-600">📋</span>
                  <span>Plantilla Seleccionada</span>
                </h3>
                <div className="p-4 border border-blue-200 rounded-lg bg-blue-50">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-blue-600 text-xl">📄</span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">{templateDocx.name}</p>
                        <p className="text-sm text-gray-600">Documento .docx con placeholders</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={removeTemplate}
                      className="text-red-600 hover:text-red-800 text-sm px-3 py-2 rounded-md hover:bg-red-50 transition-colors border border-red-200 hover:border-red-300"
                    >
                      🗑️ Eliminar
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Example descriptions */}
            {examples.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
                  <span className="text-green-600">📄</span>
                  <span>Descripciones de Ejemplos</span>
                </h3>
                <div className="space-y-3">
                  {examples.map((file, index) => (
                    <div
                      key={`example-${index}`}
                      className="p-4 border border-green-200 rounded-lg bg-green-50"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                            <span className="text-green-600 text-sm">📄</span>
                          </div>
                          <div>
                            <p className="font-medium text-gray-800">{file.name}</p>
                            <p className="text-xs text-gray-600">Archivo de ejemplo</p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeExample(index)}
                          className="text-red-600 hover:text-red-800 text-sm px-2 py-1 rounded-md hover:bg-red-50 transition-colors border border-red-200 hover:border-red-300"
                        >
                          🗑️ Eliminar
                        </button>
                      </div>
                      <textarea
                        value={exampleDescriptions[index] || ""}
                        onChange={(e) =>
                          handleExampleDescriptionChange(index, e.target.value)
                        }
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                        placeholder="Describe el propósito de este ejemplo..."
                        rows={2}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div className="flex justify-between pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={handleClear}
                className="py-3 px-6 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors border border-gray-300 hover:border-gray-400"
              >
                🗑️ Limpiar archivos
              </button>
              <button
                className="py-3 px-8 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-sm hover:shadow-md"
                type="submit"
              >
                ✨ Crear Workflow
              </button>
            </div>
          </form>
        </div>
      </Modal>
    </>
  );
};
