import { useState, useEffect, useRef } from "react";
import { Markdowner } from "../Markdowner/Markdowner";
import { Modal } from "../Modal/Modal";
import {
  API_URL,
  convertAsset,
  getSupportedExportTypes,
  requestChanges,
} from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import { toast } from "react-hot-toast";
import { generateUniqueID } from "../../utils/lib";

import socket from "../../infrastructure/socket";

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

type ExportType = {
  type: string;
  name: string;
  description: string;
};

type ExportCategory = {
  name: string;
  types: ExportType[];
};

interface AssetCardProps {
  asset: Asset;
  refetchAssets: () => void;
}

export const AssetCard = ({ asset, refetchAssets }: AssetCardProps) => {
  const [showContent, setShowContent] = useState(false);
  const [exportTypes, setExportTypes] = useState<ExportType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const { user } = useAuthStore();

  // Group export types by category
  const groupedExportTypes = (types: ExportType[]): ExportCategory[] => {
    const categories: { [key: string]: ExportType[] } = {};

    types.forEach((type) => {
      let category = "Other";

      if (["html", "pdf", "docx", "odt", "rtf", "txt"].includes(type.type)) {
        category = "Document Formats";
      } else if (
        ["md", "gfm", "commonmark", "asciidoc", "rst", "org"].includes(
          type.type
        )
      ) {
        category = "Markup Formats";
      } else if (["pptx", "odp", "beamer", "revealjs"].includes(type.type)) {
        category = "Presentation Formats";
      } else if (["epub", "latex", "tex"].includes(type.type)) {
        category = "Publishing Formats";
      } else if (["json", "yaml", "xml"].includes(type.type)) {
        category = "Data Formats";
      } else if (
        ["mediawiki", "jira", "zimwiki", "vimwiki", "xwiki"].includes(type.type)
      ) {
        category = "Wiki Formats";
      } else if (["man", "docbook4", "docbook5"].includes(type.type)) {
        category = "Documentation Formats";
      } else if (
        [
          "jats",
          "jats_archiving",
          "jats_publishing",
          "jats_articleauthoring",
        ].includes(type.type)
      ) {
        category = "Academic Formats";
      }

      if (!categories[category]) {
        categories[category] = [];
      }
      categories[category].push(type);
    });

    return Object.entries(categories).map(([name, types]) => ({
      name,
      types,
    }));
  };

  useEffect(() => {
    const loadExportTypes = async () => {
      try {
        const response = await getSupportedExportTypes();
        setExportTypes(response.supported_types || []);
      } catch (error) {
        console.error("Error loading export types:", error);
        // Fallback to common types if API fails
        setExportTypes([
          {
            type: "docx",
            name: "Word Document",
            description: "Microsoft Word format",
          },
          { type: "pdf", name: "PDF", description: "Portable Document Format" },
          { type: "html", name: "HTML", description: "Web page format" },
          {
            type: "txt",
            name: "Plain Text",
            description: "Simple text format",
          },
          { type: "md", name: "Markdown", description: "Markdown format" },
        ]);
      }
    };
    loadExportTypes();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isDropdownOpen) {
        const target = event.target as Element;
        if (!target.closest(".dropdown-container")) {
          setIsDropdownOpen(false);
        }
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isDropdownOpen]);

  const toggleContent = () => {
    setShowContent(!showContent);
  };

  const handleExport = async (exportType: string) => {
    if (!user?.email) {
      toast.error("Usuario no autenticado");
      return;
    }

    setIsLoading(true);
    const tid = toast.loading("Convirtiendo y descargando...");

    try {
      const response = await convertAsset(asset.id, user.email, exportType);

      if (response.retrieve_url) {
        window.open(API_URL + response.retrieve_url, "_blank");
        toast.success("Archivo descargado correctamente", { id: tid });
      } else {
        toast.error("Error al descargar el archivo", { id: tid });
      }
    } catch (error) {
      console.error("Error exporting asset:", error);
      toast.error("Error al convertir el archivo", { id: tid });
    } finally {
      setIsLoading(false);
      setIsDropdownOpen(false);
    }
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
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              ) : (
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
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
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
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
          <h3 className="text-xl font-bold text-center text-gray-900">
            {asset.name}
          </h3>
          <div className="flex justify-end gap-2 items-center mb-6">
            {/* Modern Dropdown */}
            <div>
              <div className="relative dropdown-container">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsDropdownOpen(!isDropdownOpen);
                  }}
                  disabled={isLoading}
                  className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 shadow-lg ${
                    isLoading
                      ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                      : "bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 hover:shadow-xl transform "
                  }`}
                >
                  {isLoading ? (
                    <>
                      <svg
                        className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Procesando...
                    </>
                  ) : (
                    <>
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
                          d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                      Exportar como...
                      <svg
                        className={`w-4 h-4 transition-transform duration-200 ${
                          isDropdownOpen ? "rotate-180" : ""
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </>
                  )}
                </button>

                {/* Dropdown Menu */}
                {isDropdownOpen && !isLoading && (
                  <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-2xl border border-gray-200/60 z-50 overflow-hidden max-h-96 overflow-y-auto">
                    <div className="p-3">
                      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-3 py-2 bg-gray-50 rounded-lg mb-3">
                        Formatos disponibles
                      </div>
                      {groupedExportTypes(exportTypes).map((category) => (
                        <div key={category.name} className="mb-4 last:mb-0">
                          <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider px-3 py-2 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg mb-2">
                            {category.name}
                          </div>
                          <div className="space-y-1">
                            {category.types.map((exportType) => (
                              <button
                                key={exportType.type}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleExport(exportType.type);
                                }}
                                className="w-full text-left px-3 py-3 rounded-lg hover:bg-gradient-to-r hover:from-blue-50 hover:to-blue-100 transition-all duration-150 group border border-transparent hover:border-blue-200"
                              >
                                <div className="flex items-center justify-between">
                                  <div className="flex-1">
                                    <div className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors flex items-center gap-2">
                                      <div className="w-2 h-2 bg-blue-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                      {exportType.name}
                                    </div>
                                    <div className="text-sm text-gray-500 group-hover:text-gray-600 mt-1">
                                      {exportType.description}
                                    </div>
                                  </div>
                                  <div className="flex-shrink-0 ml-3">
                                    <div className="text-xs font-mono text-gray-400 bg-gray-100 px-2 py-1 rounded group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
                                      .{exportType.type}
                                    </div>
                                  </div>
                                </div>
                              </button>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <ChangesRequester
              asset={asset}
              onFinish={() => {
                refetchAssets();
              }}
            />
            <div>
              <button className="bg-red-500 text-white px-4 py-2 rounded-xl">
                Eliminar
              </button>
            </div>
          </div>

          {/* Content Preview */}
          <div className="prose prose-sm max-w-none bg-gradient-to-br from-gray-50 to-white rounded-xl p-6 overflow-auto border border-gray-200/60 shadow-xl">
            <Markdowner markdown={asset.content} />
          </div>
        </Modal>
      )}
    </>
  );
};

const ChangesRequester = ({
  asset,
  onFinish,
}: {
  asset: Asset;
  onFinish: () => void;
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const { user } = useAuthStore();
  const [not_id, setNotId] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleRequestChanges = async (
    e: React.MouseEvent<HTMLButtonElement>
  ) => {
    e.preventDefault();
    if (textareaRef.current) {
      const text = textareaRef.current.value;
      console.log(text);
      if (text.length > 0) {
        const _not_id = generateUniqueID("not_");
        try {
          await requestChanges(asset.id, text, user?.email || "", _not_id);
          setNotId(_not_id);
          setIsOpen(false);
        } catch (error) {
          console.error("Error requesting changes:", error);
          toast.error("Error al solicitar cambios");
        }
      } else {
        toast.error("Por favor, describe los cambios que deseas realizar");
      }
    }
  };

  useEffect(() => {
    if (not_id) {
      socket.connect();
      socket.on(`notification_${not_id}`, (data) => {
        console.log(data);
        if (data.status === "DONE") {
          toast.success("Cambios realizados correctamente");
          onFinish();
        }
      });
    }
    return () => {
      if (not_id) {
        socket.off(`notification_${not_id}`);
        socket.disconnect();
      }
    };
  }, [not_id]);
  return (
    <>
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded-xl flex items-center gap-2 hover:bg-blue-700"
        onClick={() => setIsOpen(!isOpen)}
      >
        Solicita cambios
      </button>
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <h3 className="text-xl font-bold text-center text-gray-900">
          Solicita cambios al agente IA
        </h3>
        <div>
          <textarea
            ref={textareaRef}
            className="w-full h-48 p-2 border border-gray-300 rounded-xl"
            placeholder="Describe los cambios que deseas realizar"
          />
        </div>
        <div className="flex justify-end gap-2 items-center mb-6">
          <button
            onClick={() => setIsOpen(false)}
            className="bg-red-500 text-white px-4 py-2 rounded-xl"
          >
            Cancelar
          </button>
          <button
            onClick={handleRequestChanges}
            className="bg-blue-500 text-white px-4 py-2 rounded-xl"
          >
            Solicitar cambios
          </button>
        </div>
      </Modal>
    </>
  );
};
