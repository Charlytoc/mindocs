import { useState } from "react";
import { Markdowner } from "../Markdowner/Markdowner";
import { Modal } from "../Modal/Modal";
import { deleteAsset } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import { toast } from "react-hot-toast";
import { AssetExporter } from "./AssetExporter";
import { AssetChat } from "./AssetChat";

// Lucide React Icons - Modern, lightweight icon library
import {
  Eye,
  Zap,
  FileText,
  Trash2,
  Check,
  X,
  MessageCircle,
} from "lucide-react";

type Asset = {
  id: string;
  name: string;
  description?: string;
  content: string;
  extracted_text?: string;
  type?: string;
  origin?: "uploaded" | "generated";
  _group?: string;
};

interface AssetCardProps {
  asset: Asset;
  refetchAssets: () => void;
}

export const AssetCard = ({ asset, refetchAssets }: AssetCardProps) => {
  const [showContent, setShowContent] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const { user } = useAuthStore();

  const toggleContent = () => {
    setShowContent(!showContent);
  };

  const handleDelete = async () => {
    if (!user?.email) {
      toast.error("Usuario no autenticado");
      return;
    }

    setIsLoading(true);
    const tid = toast.loading("Eliminando recurso...");

    try {
      await deleteAsset(asset.id, user.email);
      toast.success("Recurso eliminado correctamente", { id: tid });
      setShowContent(false); // Cerrar el modal
      refetchAssets();
    } catch (error) {
      console.error("Error deleting asset:", error);
      toast.error("Error al eliminar el recurso", { id: tid });
    } finally {
      setIsLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  const confirmDelete = () => {
    setShowDeleteConfirm(true);
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  const isUploaded = asset.origin === "uploaded";

  return (
    <>
      <div
        className={`group relative overflow-hidden rounded-2xl bg-gradient-to-br from-white to-gray-50/50 border border-gray-200/60 shadow-lg hover:shadow-2xl transition-all duration-300 ease-out cursor-pointer transform hover:-translate-y-1 hover:scale-[1.02] ${
          isUploaded
            ? "hover:border-blue-300/80 hover:shadow-blue-100/50"
            : "hover:border-green-300/80 hover:shadow-green-100/50"
        }`}
        onClick={toggleContent}
      >
        {/* Background gradient overlay */}
        <div
          className={`absolute inset-0 bg-gradient-to-br opacity-5 ${
            isUploaded
              ? "from-blue-400 to-blue-600"
              : "from-green-400 to-green-600"
          }`}
        />

        {/* Status badge */}
        <div className="absolute top-1 right-1 z-10">
          <span
            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold shadow-sm backdrop-blur-sm ${
              isUploaded
                ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-blue-200/50"
                : "bg-gradient-to-r from-green-500 to-green-600 text-white shadow-green-200/50"
            }`}
          >
            {isUploaded ? "Subido" : "Generado"}
          </span>
        </div>

        {/* Content */}
        <div className="relative z-10 p-6">
          {/* Icon and title */}
          <div className="flex items-start gap-3 mb-4">
            <div
              className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center shadow-lg ${
                isUploaded
                  ? "bg-gradient-to-br from-blue-500 to-blue-600 shadow-blue-200/50"
                  : "bg-gradient-to-br from-green-500 to-green-600 shadow-green-200/50"
              }`}
            >
              {isUploaded ? (
                <Eye className="w-6 h-6 text-white" />
              ) : (
                <Zap className="w-6 h-6 text-white" />
              )}
            </div>

            <div className="flex-1 min-w-0">
              <h4 className="text-lg font-bold text-gray-900 mb-1 truncate group-hover:text-gray-700 transition-colors">
                {asset.name}
              </h4>
              {asset.description && (
                <p className="text-sm text-gray-600 font-medium">
                  {asset.description}
                </p>
              )}
            </div>
          </div>

          {/* Action button */}
          {asset.content && (
            <div className="mt-4">
              <button
                className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 ${
                  isUploaded
                    ? "bg-gradient-to-r from-blue-50 to-blue-100 text-blue-700 hover:from-blue-100 hover:to-blue-200 hover:shadow-md"
                    : "bg-gradient-to-r from-green-50 to-green-100 text-green-700 hover:from-green-100 hover:to-green-200 hover:shadow-md"
                }`}
              >
                <FileText className="w-4 h-4" />
                Ver contenido
              </button>
            </div>
          )}
        </div>

        {/* Hover effect overlay */}
        <div
          className={`absolute inset-0 bg-gradient-to-t from-black/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${
            isUploaded ? "from-blue-500/10" : "from-green-500/10"
          }`}
        />
      </div>

      {showContent && (
        <Modal isOpen={showContent} onClose={toggleContent}>
          <h3 className="text-xl font-bold text-center text-gray-900 truncate">
            {asset.name}
          </h3>

          {/* Action Buttons - Improved Styling */}
          <div className="flex justify-between gap-3 items-center mb-6 p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl">
            {/* Delete Button */}
            <div className="flex-1">
              {!showDeleteConfirm ? (
                <button
                  className="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-4 py-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center gap-2 font-semibold"
                  onClick={confirmDelete}
                  disabled={isLoading}
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              ) : (
                <div className="flex gap-2">
                  <button
                    className="flex-1 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-4 py-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center gap-2 font-semibold"
                    onClick={handleDelete}
                    disabled={isLoading}
                  >
                    <Check className="w-5 h-5" />
                    {isLoading ? "Eliminando..." : "Eliminar"}
                  </button>
                  <button
                    className="flex-1 bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 text-white px-4 py-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center gap-2 font-semibold"
                    onClick={cancelDelete}
                    disabled={isLoading}
                  >
                    <X className="w-5 h-5" />
                    Cancelar
                  </button>
                </div>
              )}
            </div>

            {/* Chat Button */}
            {asset.content && !showDeleteConfirm && (
              <button
                className="flex-1 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white px-4 py-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center gap-2 font-semibold"
                onClick={() => setShowChat(true)}
              >
                <MessageCircle className="w-5 h-5" />
              </button>
            )}

            {/* Export Button */}
            {!showDeleteConfirm && (
              <div className="flex-1">
                <AssetExporter assetId={asset.id} />
              </div>
            )}
          </div>

          {/* Content Preview */}
          <div className="prose prose-sm max-w-none bg-gradient-to-br from-gray-50 to-white rounded-xl p-6 overflow-auto border border-gray-200/60 shadow-xl">
            <Markdowner markdown={asset.content} />
          </div>
        </Modal>
      )}

      {/* Chat Modal */}
      {showChat && (
        <Modal isOpen={showChat} onClose={() => setShowChat(false)}>
          <AssetChat
            asset={asset}
            onFinish={() => {
              refetchAssets();
              setShowChat(false);
            }}
            onClose={() => setShowChat(false)}
          />
        </Modal>
      )}
    </>
  );
};
