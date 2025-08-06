import { useParams } from "react-router";

import { useEffect, useState } from "react";
import {
  getWorkflowExecution,
  getWorkflowExecutionAssets,
} from "../../../utils/api";
import { useAuthStore } from "../../../infrastructure/store";
import { Waiter } from "../../../components/Waiter/Waiter";
import { AssetList } from "../../../components/Assets";
import { rerunWorkflowExecution } from "../../../utils/api";

type Asset = {
  id: string;
  name: string;
  description?: string;
  content: string;
  extracted_text?: string;
  type?: string;
  origin?: "uploaded" | "generated";
};

type WorkflowExecution = {
  id: string;
  workflow: { id: string; name: string };
  status: string;
  log: string;
  created_at: string;
  started_at: string;
  finished_at: string;
  messages: Message[];
};

type Message = {
  id: string;
  role: string;
  content: string;
};

export const WorkflowExecutionDetail = () => {
  const { execution_id } = useParams();
  const { user } = useAuthStore();

  const [uploadedAssets, setUploadedAssets] = useState<Asset[]>([]);
  const [generatedAssets, setGeneratedAssets] = useState<Asset[]>([]);
  const [execution, setExecution] = useState<WorkflowExecution | null>(null);

  // Fetch both asset types
  const fetchAssets = async () => {
    if (!execution_id || !user?.email) return;
    const assetsData = await getWorkflowExecutionAssets(
      execution_id,
      user.email
    );
    setUploadedAssets(
      (assetsData.uploaded || []).map((a: any) => ({
        ...a,
        origin: "uploaded",
      }))
    );
    setGeneratedAssets(
      (assetsData.generated || []).map((a: any) => ({
        ...a,
        origin: "generated",
      }))
    );
  };

  const fetchExecution = async () => {
    if (!execution_id || !user?.email) return;
    const executionData = await getWorkflowExecution(execution_id, user.email);
    setExecution(executionData);
    if (executionData.status === "DONE") {
      fetchAssets();
    }
  };

  useEffect(() => {
    fetchExecution();
  }, [execution_id, user?.email]);

  useEffect(() => {
    if (execution?.status === "DONE") {
      fetchAssets();
    }
  }, [execution?.status]);

  // Unifica ambos assets para mostrar en una sola lista
  const allAssets = [
    ...uploadedAssets.map((a) => ({ ...a, _group: "Subidos" })),
    ...generatedAssets.map((a) => ({ ...a, _group: "Generados" })),
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "DONE":
        return "bg-gradient-to-r from-green-500 to-green-600 text-white shadow-green-200/50";
      case "IN_PROGRESS":
        return "bg-gradient-to-r from-yellow-500 to-yellow-600 text-white shadow-yellow-200/50";
      case "PENDING":
        return "bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-blue-200/50";
      default:
        return "bg-gradient-to-r from-gray-500 to-gray-600 text-white shadow-gray-200/50";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50/50">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header Section */}

        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            {execution?.workflow.name}
          </h1>
          <div className="text-center">
            <div className="flex items-center justify-center gap-4 mb-6">
              {execution?.finished_at && (
                <span className="text-sm text-gray-500 font-medium">
                  Terminado el{" "}
                  {new Date(execution.finished_at).toLocaleString()}
                </span>
              )}
              <span
                className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold shadow-lg ${getStatusColor(
                  execution?.status || ""
                )}`}
              >
                {execution?.status}
              </span>
              <button
                className="border border-gray-300 rounded-full px-4 py-2 hover:bg-gray-100 cursor-pointer"
                onClick={async () => {
                  await rerunWorkflowExecution(
                    execution_id || "",
                    user?.email || ""
                  );
                  fetchExecution();
                }}
              >
                🔄
              </button>
            </div>

            {/* Progress indicator for in-progress workflows */}
          </div>
        </div>
        {execution &&
          (execution.status === "IN_PROGRESS" ||
            execution.status === "PENDING") && (
            <div className="mt-6 p-4 bg-white rounded-2xl shadow-lg border border-gray-200/60">
              <Waiter
                executionId={execution_id || ""}
                onFinish={fetchExecution}
              />
            </div>
          )}

        {execution?.status === "DONE" && (
          <div className="space-y-8">
            {/* Section Title */}
            <p className="text-gray-600">
              Archivos subidos y documentos generados por el proceso
            </p>
            {/* <LogInspector log={execution?.log || ""} /> */}
            {/* <MessagesList messages={execution?.messages || []} /> */}

            {/* Assets Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <AssetList assets={allAssets} refetchAssets={fetchAssets} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// const LogInspector = ({ log }: { log: string }) => {
//   const [isOpen, setIsOpen] = useState(false);
//   return (
//     <>
//       <button onClick={() => setIsOpen(true)}>Ver Log</button>
//       <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
//         <div className="p-4">
//           <h2 className="text-lg font-bold text-gray-900 mb-2">
//             Log del Workflow
//           </h2>
//           <pre className="text-sm text-gray-600 whitespace-pre-wrap break-words">
//             {log}
//           </pre>
//         </div>
//       </Modal>
//     </>
//   );
// };

// const MessagesList = ({ messages }: { messages: Message[] }) => {
//   return (
//     <div>
//       {messages.map((m) => (
//         <div key={m.id}>
//           <span className="font-bold">{m.role}:</span> {m.content}
//         </div>
//       ))}
//     </div>
//   );
// };
