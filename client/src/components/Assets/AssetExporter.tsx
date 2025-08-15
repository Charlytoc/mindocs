import { useState, useEffect } from "react";
import { Download, ChevronDown, Loader2 } from "lucide-react";
import {
  API_URL,
  convertAsset,
  getSupportedExportTypes,
} from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import { toast } from "react-hot-toast";

type ExportType = {
  type: string;
  name: string;
  description: string;
};

type ExportCategory = {
  name: string;
  types: ExportType[];
};

interface AssetExporterProps {
  assetId: string;
}

export const AssetExporter = ({ assetId }: AssetExporterProps) => {
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

  const handleExport = async (exportType: string) => {
    if (!user?.email) {
      toast.error("Usuario no autenticado");
      return;
    }

    setIsLoading(true);
    const tid = toast.loading("Convirtiendo y descargando...");

    try {
      const response = await convertAsset(assetId, user.email, exportType);

      if (response.retrieve_url) {
        const downloadUrl = `${API_URL}${response.retrieve_url}`;
        window.open(downloadUrl, "_blank");
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

  return (
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
            : "bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 hover:shadow-xl transform hover:scale-105"
        }`}
      >
        {isLoading ? (
          <>
            <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" />
            Procesando...
          </>
        ) : (
          <>
            <Download className="w-4 h-4" />
            Exportar
            <ChevronDown
              className={`w-4 h-4 transition-transform duration-200 ${
                isDropdownOpen ? "rotate-180" : ""
              }`}
            />
          </>
        )}
      </button>

      {/* Dropdown Menu */}
      {isDropdownOpen && !isLoading && (
        <div className="absolute right-0 mt-2 w-72 sm:w-80 lg:w-96 bg-white rounded-xl shadow-2xl border border-gray-200/60 z-50 overflow-hidden max-h-80 overflow-y-auto">
          <div className="p-4">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-3 py-2 bg-gray-50 rounded-lg mb-4 text-center">
              Formatos disponibles
            </div>
            {groupedExportTypes(exportTypes).map((category) => (
              <div key={category.name} className="mb-5 last:mb-0">
                <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider px-3 py-2 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg mb-3">
                  {category.name}
                </div>
                <div className="space-y-2">
                  {category.types.map((exportType) => (
                    <button
                      key={exportType.type}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleExport(exportType.type);
                      }}
                      className="w-full text-left px-4 py-3 rounded-lg hover:bg-gradient-to-r hover:from-blue-50 hover:to-blue-100 transition-all duration-150 group border border-transparent hover:border-blue-200"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors flex items-center gap-2 mb-1">
                            <div className="w-2 h-2 bg-blue-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"></div>
                            <span className="truncate">{exportType.name}</span>
                          </div>
                        </div>
                        <div className="flex-shrink-0 ml-4">
                          <div className="text-xs font-mono text-gray-400 bg-gray-100 px-3 py-1 rounded-md group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors whitespace-nowrap">
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
  );
};
