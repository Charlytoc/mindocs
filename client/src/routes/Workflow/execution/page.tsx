import { useParams } from "react-router";

import { useEffect, useState } from "react";
import {
  getWorkflowExecution,
  getWorkflowExecutionAssets,
} from "../../../utils/api";
import { useAuthStore } from "../../../infrastructure/store";
import { Waiter } from "../../../components/Waiter/Waiter";
import { AssetList } from "../../../components/Assets";

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
  created_at: string;
  started_at: string;
  finished_at: string;
};

export const WorkflowExecutionDetail = () => {
  const { id, execution_id } = useParams();
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
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg shadow-blue-200/50 mb-6">
            <svg
              className="w-8 h-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          </div>

          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {execution?.workflow.name}
          </h1>

          <div className="flex items-center justify-center gap-4 mb-6">
            <span className="text-sm text-gray-500 font-medium">
              ID: #{execution_id}
            </span>
            <span
              className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold shadow-lg ${getStatusColor(
                execution?.status || ""
              )}`}
            >
              {execution?.status}
            </span>
          </div>

          {/* Progress indicator for in-progress workflows */}
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
        </div>

        {/* Assets Grid */}
        {execution?.status === "DONE" && (
          <div className="space-y-8">
            {/* Section Title */}
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Documentos del Workflow
              </h2>
              <p className="text-gray-600">
                Archivos subidos y documentos generados por el proceso
              </p>
            </div>

            {/* Assets Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <AssetList assets={allAssets} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
