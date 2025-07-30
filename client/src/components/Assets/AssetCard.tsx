import { useState } from "react";
import { Markdowner } from "../Markdowner/Markdowner";
import { Modal } from "../Modal/Modal";

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
}

export const AssetCard = ({ asset }: AssetCardProps) => {
  const [showContent, setShowContent] = useState(false);
  const [showExtractedText, setShowExtractedText] = useState(false);

  const toggleContent = () => {
    setShowContent(!showContent);
  };

  const toggleExtractedText = () => {
    setShowExtractedText(!showExtractedText);
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
          <div className="prose prose-sm max-w-none bg-gradient-to-br from-gray-50 to-white rounded-xl p-6 overflow-auto border border-gray-200/60 shadow-xl">
            <Markdowner markdown={asset.content} />
          </div>
        </Modal>
      )}
    </>
  );
};
