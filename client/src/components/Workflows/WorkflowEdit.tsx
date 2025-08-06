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
            Instrucciones
          </label>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Instrucciones para el workflow"
            rows={6}
          />
          <p className="text-sm text-gray-500 mt-1">
            Las instrucciones ayudan a la IA a entender cómo procesar los
            archivos
          </p>
        </div>

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
