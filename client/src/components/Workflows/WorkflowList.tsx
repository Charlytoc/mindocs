import { useState, useEffect } from "react";
import { deleteWorkflow, getWorkflows } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import toast from "react-hot-toast";

interface Workflow {
  id: string;
  name: string;
  description: string;
}

interface WorkflowListProps {
  onSelectWorkflow: (workflow: Workflow) => void;
}

export const WorkflowList = ({ onSelectWorkflow }: WorkflowListProps) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();

  useEffect(() => {
    const fetchWorkflows = async () => {
      if (!user) return;

      try {
        setLoading(true);
        const data = await getWorkflows(user.email);
        setWorkflows(data);
      } catch (error) {
        toast.error("Error al cargar los workflows");
        console.error("Error fetching workflows:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkflows();
  }, [user]);

  const handleDeleteWorkflow = async (workflowId: string) => {
    try {
      if (!user) return;
      try {
        await deleteWorkflow(workflowId, user.email);
        toast.success("Workflow eliminado correctamente");
        setWorkflows(
          workflows.filter((workflow) => workflow.id !== workflowId)
        );
      } catch (error) {
        toast.error("Error al eliminar el workflow");
      }
    } catch (error) {
      toast.error("Error al eliminar el workflow");
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando workflows...</p>
        </div>
      </div>
    );
  }

  if (workflows.length === 0) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="text-gray-400 mb-4">
            <svg
              className="w-16 h-16 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">
            No hay workflows disponibles
          </h2>
          <p className="text-gray-600 mb-4">
            Parece que aún no tienes workflows configurados. Crea uno para
            empezar.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflows.map((workflow) => (
            <div
              key={workflow.id}
              className="bg-white rounded-2xl shadow-xl p-6 cursor-pointer hover:shadow-2xl transition-all duration-300 hover:scale-101 border border-gray-200"
            >
              <div
                className="text-blue-600 mb-4"
                onClick={() => onSelectWorkflow(workflow)}
              >
                <svg
                  className="w-12 h-12"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                  />
                </svg>
              </div>

              <h3 className="text-xl font-bold text-gray-800 mb-2">
                {workflow.name}
              </h3>

              {workflow.description && (
                <p className="text-gray-600 mb-4">{workflow.description}</p>
              )}

              <div className="flex justify-between">
                <div
                  className="flex items-center text-blue-600 font-medium"
                  onClick={() => onSelectWorkflow(workflow)}
                >
                  <span>Seleccionar</span>
                  <svg
                    className="w-4 h-4 ml-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
                <div
                  className="flex items-center text-red-600 font-medium gap-2"
                  onClick={() => handleDeleteWorkflow(workflow.id)}
                >
                  <svg
                    className="w-4 h-4 ml-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                  <span>Eliminar</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
