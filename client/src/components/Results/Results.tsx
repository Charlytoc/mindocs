import { useState, useEffect } from "react";
import {
  getCaseResults,
  updateDemand,
  updateAgreement,
  requestAIChanges,
  approveCase,
} from "../../utils/api";
import { RichTextEditor } from "./RichTextEditor";
import toast from "react-hot-toast";

type ResultsProps = {
  caseId: string;
};

type CaseResults = {
  demand?: string;
  agreement?: string;
  summary?: string;
};

export const Results = ({ caseId }: ResultsProps) => {
  const [results, setResults] = useState<CaseResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"demand" | "agreement">("demand");
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isRequestingAI, setIsRequestingAI] = useState(false);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true);
        const data = await getCaseResults(caseId);
        console.log("Results:", data);
        setResults(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error desconocido");
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [caseId]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleSave = async (content: string) => {
    try {
      setIsSaving(true);

      if (activeTab === "demand") {
        await updateDemand(caseId, content);
        setResults((prev) => (prev ? { ...prev, demand: content } : null));
        toast.success("Demanda actualizada exitosamente");
      } else {
        await updateAgreement(caseId, content);
        setResults((prev) => (prev ? { ...prev, agreement: content } : null));
        toast.success("Convenio actualizado exitosamente");
      }

      setIsEditing(false);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setIsSaving(false);
    }
  };

  const handleRequestAIChanges = async (feedback: string) => {
    try {
      setIsRequestingAI(true);
      await requestAIChanges(caseId, activeTab, feedback);
      toast.success("Solicitud enviada a la IA exitosamente");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Error al enviar solicitud a la IA"
      );
    } finally {
      setIsRequestingAI(false);
    }
  };

  const handleApproveCase = async () => {
    try {
      await approveCase(caseId);
      toast.success("Caso aprobado exitosamente");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Error al aprobar el caso"
      );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando resultados...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center ">
          <div className="text-red-500 mb-4">
            <svg
              className="w-12 h-12 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <p className="text-gray-600">No se encontraron resultados</p>
        </div>
      </div>
    );
  }

  const currentContent =
    activeTab === "demand" ? results.demand : results.agreement;
  const hasContent = currentContent && currentContent.trim() !== "";

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto ">
        {/* Tabs */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => {
                setActiveTab("demand");
                setIsEditing(false);
              }}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === "demand"
                  ? "bg-blue-50 text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              Escrito Inicial
            </button>
            <button
              onClick={() => {
                setActiveTab("agreement");
                setIsEditing(false);
              }}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === "agreement"
                  ? "bg-blue-50 text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              Convenio
            </button>
          </div>

          {/* Content */}
          <div className="p-6 bg-gray-100">
            {hasContent ? (
              isEditing ? (
                <RichTextEditor
                  initialValue={currentContent || ""}
                  onSave={handleSave}
                  onCancel={handleCancelEdit}
                  onRequestAIChanges={handleRequestAIChanges}
                  isSaving={isSaving}
                  isRequestingAI={isRequestingAI}
                />
              ) : (
                <div className="space-y-4 ">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-800">
                      {activeTab === "demand" ? "Escrito Inicial" : "Convenio"}
                    </h3>
                    <button
                      onClick={handleEdit}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                        />
                      </svg>
                      Editar
                    </button>
                  </div>
                  <div
                    className="bg-gray-50 rounded-lg p-6 border border-gray-200 prose max-w-[816px] mx-auto"
                    dangerouslySetInnerHTML={{ __html: currentContent || "" }}
                  />
                </div>
              )
            ) : (
              <div className="text-center py-12">
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
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <p className="text-gray-500">
                  {activeTab === "demand"
                    ? "No hay demanda disponible"
                    : "No hay convenio disponible"}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-6 mt-6">
          <div className="flex justify-center gap-4">
            <button
              onClick={() => (window.location.href = "/")}
              className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Generar Nuevo Caso
            </button>
            <button
              onClick={handleApproveCase}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              OK
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
