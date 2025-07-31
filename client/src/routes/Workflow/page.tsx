import { useNavigate, useParams } from "react-router";
import { WorkflowUpload } from "../../components/Workflows/WorkflowUpload";
import { WorkflowExecutions } from "../../components/Workflows/WorkflowExecutions";
import { useEffect, useState } from "react";
import { WorkflowEdit } from "../../components/Workflows/WorkflowEdit";
import { getWorkflow } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import { Navigation } from "../../components/Navigation/Navigation";

export type WorkflowExecution = {
  id: string;
  status: string;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  summary: string | null;
  status_message: string | null;
  delivered: boolean;
};

export type Workflow = {
  id: string;
  name: string;
  description: string;
  instructions: string;
  executions: WorkflowExecution[];
};

export const WorkflowDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchWorkflow();
  }, [id]);

  const fetchWorkflow = async () => {
    const workflow = await getWorkflow(id || "", user?.email || "");
    setWorkflow(workflow);
  };
  const handleExecutionClick = (executionId: string) => {
    navigate(`/workflow/${id}/execution/${executionId}`);
  };

  const handleEditSave = (updatedWorkflow: Workflow) => {
    setWorkflow(updatedWorkflow);
    setIsEditing(false);
  };

  const handleEditCancel = () => {
    setIsEditing(false);
  };

  if (!workflow) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <p className="text-center text-gray-500">Cargando workflow...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {isEditing ? (
            <WorkflowEdit
              workflow={workflow}
              onSave={handleEditSave}
              onCancel={handleEditCancel}
            />
          ) : (
            <>
              {/* Header con botón de editar */}
              <div className="bg-white rounded-2xl shadow-xl p-4">
                <div className="flex flex-row justify-between items-start">
                  <div className="flex flex-col items-start gap-2">
                    <h2 className="text-2xl font-bold text-gray-800 ">
                      {workflow.name}
                    </h2>
                  </div>

                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Editar
                  </button>
                </div>
              </div>

              {/* Formulario de upload */}
              <WorkflowUpload
                // fetchWorkflow={fetchWorkflow}
                workflow={{
                  id: id || "",
                  name: workflow?.name || "",
                  description: workflow?.description || "",
                }}
                onUploadSuccess={({ execution_id }) => {
                  navigate(`/workflow/${id}/execution/${execution_id}`);
                }}
                onBack={() => {}}
              />

              {/* Mostrar ejecuciones recientes */}
              <WorkflowExecutions
                fetchWorkflow={fetchWorkflow}
                executions={workflow.executions}
                onExecutionClick={handleExecutionClick}
              />
            </>
          )}
        </div>
      </div>
    </>
  );
};
