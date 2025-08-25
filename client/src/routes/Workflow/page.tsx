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

export type WorkflowExample = {
  id: string;
  name: string;
  description: string | null;
  content: string;
  is_template: boolean;
  format: string | null;
};

export type Workflow = {
  id: string;
  name: string;
  description: string;
  instructions: string;
  executions: WorkflowExecution[];
  examples: WorkflowExample[];
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
    console.log(workflow, "workflow");
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

  const handleDownloadFile = async (filePath: string, fileName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/download-file?path=${encodeURIComponent(filePath)}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Error downloading file');
      }
    } catch (error) {
      console.error('Error downloading file:', error);
    }
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
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <div className="flex flex-row justify-between items-start mb-4">
                  <div className="flex flex-col items-start gap-2">
                    <h2 className="text-2xl font-bold text-gray-800 ">
                      {workflow.name}
                    </h2>
                    {workflow.description && (
                      <p className="text-gray-600 max-w-2xl">{workflow.description}</p>
                    )}
                  </div>

                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Editar
                  </button>
                </div>
              </div>

              {/* Workflow Statistics */}
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">📊 Estadísticas del Workflow</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="text-2xl font-bold text-blue-600">
                      {workflow.examples ? workflow.examples.filter(ex => ex.is_template).length : 0}
                    </div>
                    <div className="text-sm text-blue-800">Plantillas</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="text-2xl font-bold text-green-600">
                      {workflow.examples ? workflow.examples.filter(ex => !ex.is_template).length : 0}
                    </div>
                    <div className="text-sm text-green-800">Ejemplos</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <div className="text-2xl font-bold text-purple-600">
                      {workflow.executions ? workflow.executions.length : 0}
                    </div>
                    <div className="text-sm text-purple-800">Ejecuciones</div>
                  </div>
                </div>
              </div>
              <WorkflowUpload
                workflow={{
                  id: id || "",
                  name: workflow?.name || "",
                  description: workflow?.description || "",
                }}
                onUploadSuccess={({ execution_id }) => {
                  navigate(`/workflow/${id}/execution/${execution_id}`);
                }}
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
