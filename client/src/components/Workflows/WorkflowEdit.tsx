import { useState, useEffect } from "react";
import { updateWorkflow } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import toast from "react-hot-toast";
import { Workflow } from "../../routes/Workflow/page";

interface WorkflowEditProps {
  workflow: Workflow;
  onSave: (updatedWorkflow: Workflow) => void;
  onCancel: () => void;
}

export const WorkflowEdit = ({
  workflow,
  onSave,
  onCancel,
}: WorkflowEditProps) => {
  const [name, setName] = useState(workflow.name);
  const [description, setDescription] = useState(workflow.description || "");
  const [instructions, setInstructions] = useState(workflow.instructions || "");
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuthStore();

  useEffect(() => {
    setName(workflow.name);
    setDescription(workflow.description || "");
    setInstructions(workflow.instructions || "");
  }, [workflow]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!user) {
      toast.error("Debes estar autenticado para continuar");
      return;
    }

    if (!name.trim()) {
      toast.error("El nombre del workflow es obligatorio");
      return;
    }

    setIsLoading(true);

    try {
      await updateWorkflow(
        workflow.id,
        name.trim(),
        description.trim(),
        instructions.trim(),
        user.email
      );

      toast.success("Workflow actualizado correctamente");
      onSave({
        ...workflow,
        name: name.trim(),
        description: description.trim(),
        instructions: instructions.trim(),
      });
    } catch (error) {
      console.error("Error al actualizar workflow:", error);
      toast.error("Error al actualizar el workflow");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Editar Workflow
        </h2>
        <p className="text-gray-600">Modifica la información de tu workflow</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nombre del Workflow *
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Nombre del workflow"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Descripción
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Descripción del workflow"
            rows={3}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Instrucciones para la IA
          </label>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Instrucciones específicas para el agente IA"
            rows={6}
          />
          <p className="text-sm text-gray-500 mt-1">
            Las instrucciones ayudan a la IA a entender cómo procesar los archivos y qué formato de salida generar
          </p>
        </div>

        {/* Template y Ejemplos (solo lectura) */}
        {workflow.examples && workflow.examples.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">📁 Archivos del Workflow</h3>
            
            <div className="space-y-3">
              {/* Template */}
              {workflow.examples.filter(ex => ex.is_template).map((template) => (
                <div key={template.id} className="p-4 border border-blue-200 rounded-lg bg-blue-50">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                      <span className="text-blue-600 text-sm">📋</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-gray-800">{template.name}</h4>
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                          Plantilla
                        </span>
                      </div>
                      {template.description && (
                        <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                      )}
                      <p className="text-xs text-gray-500 mt-1">Formato: {template.format || 'N/A'}</p>
                    </div>
                  </div>
                </div>
              ))}

              {/* Examples */}
              {workflow.examples.filter(ex => !ex.is_template).map((example) => (
                <div key={example.id} className="p-4 border border-green-200 rounded-lg bg-green-50">
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-green-100 rounded-lg flex items-center justify-center">
                      <span className="text-green-600 text-xs">📄</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-gray-800">{example.name}</h4>
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                          Ejemplo
                        </span>
                      </div>
                      {example.description && (
                        <p className="text-sm text-gray-600 mt-1">{example.description}</p>
                      )}
                      <p className="text-xs text-gray-500 mt-1">Formato: {example.format || 'N/A'}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
              <p className="text-sm text-gray-600">
                💡 <strong>Nota:</strong> Los archivos (plantilla y ejemplos) no se pueden editar desde aquí. 
                Para cambiar los archivos, necesitarás crear un nuevo workflow.
              </p>
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-4 pt-6">
          <button
            type="button"
            onClick={onCancel}
            className="py-2 px-4 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 transition-colors"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isLoading || !name.trim()}
            className="py-2 px-4 bg-blue-600 text-white font-semibold rounded-lg shadow-md cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
          >
            {isLoading ? "Guardando..." : "Guardar Cambios"}
          </button>
        </div>
      </form>
    </div>
  );
};
