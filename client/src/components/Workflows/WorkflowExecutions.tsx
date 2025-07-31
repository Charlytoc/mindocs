import toast from "react-hot-toast";
import { useAuthStore } from "../../infrastructure/store";
import { WorkflowExecution } from "../../routes/Workflow/page";
import { deleteWorkflowExecution } from "../../utils/api";

interface WorkflowExecutionsProps {
  executions: WorkflowExecution[];
  onExecutionClick: (executionId: string) => void;
  fetchWorkflow: () => void;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case "DONE":
      return "bg-green-100 text-green-800";
    case "ERROR":
      return "bg-red-100 text-red-800";
    case "IN_PROGRESS":
      return "bg-blue-100 text-blue-800";
    case "PENDING":
      return "bg-yellow-100 text-yellow-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case "DONE":
      return "Completado";
    case "ERROR":
      return "Error";
    case "IN_PROGRESS":
      return "En Progreso";
    case "PENDING":
      return "Pendiente";
    default:
      return status;
  }
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString("es-ES", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const WorkflowExecutions = ({
  executions,
  onExecutionClick,
  fetchWorkflow,
}: WorkflowExecutionsProps) => {
  const { user } = useAuthStore();
  if (executions.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Ejecuciones Recientes
        </h2>
        <p className="text-gray-500 text-center py-8">
          No hay ejecuciones recientes para este workflow.
        </p>
      </div>
    );
  }

  const handleDelete = async (executionId: string) => {
    const toastId = toast.loading("Eliminando ejecución...");
    if (!user) {
      toast.error("Debes iniciar sesión para eliminar ejecuciones", {
        id: toastId,
      });
      return;
    }
    await deleteWorkflowExecution(executionId, user.email);
    toast.success("Ejecución eliminada correctamente", { id: toastId });
    fetchWorkflow();
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Ejecuciones Recientes ({executions.length})
      </h2>
      <div className="space-y-4">
        {executions.map((execution) => (
          <div
            key={execution.id}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                    execution.status
                  )}`}
                  onClick={() => onExecutionClick(execution.id)}
                >
                  {getStatusText(execution.status)}
                </span>
                <button
                  className="text-red-500 hover:text-red-700"
                  onClick={() => handleDelete(execution.id)}
                >
                  Eliminar
                </button>
                {execution.delivered && (
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                    Entregado
                  </span>
                )}
              </div>
            </div>

            <div className="flex space-x-4 text-xs text-gray-500 mt-3">
              {execution.started_at && (
                <span>Iniciado: {formatDate(execution.started_at)}</span>
              )}
              {execution.finished_at && (
                <span>Finalizado: {formatDate(execution.finished_at)}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
