import React, { useState, useEffect, useRef } from "react";

type RichTextEditorProps = {
  initialValue: string;
  onSave: (content: string) => Promise<void>;
  onCancel: () => void;
  onRequestAIChanges: (feedback: string) => Promise<void>;
  isSaving?: boolean;
  isRequestingAI?: boolean;
};

export const RichTextEditor: React.FC<RichTextEditorProps> = ({
  initialValue,
  onSave,
  onCancel,
  onRequestAIChanges,
  isSaving = false,
  isRequestingAI = false,
}) => {
  const [content, setContent] = useState(initialValue);
  const [aiFeedback, setAiFeedback] = useState("");
  const [showAIFeedback, setShowAIFeedback] = useState(false);
  const editorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setContent(initialValue);
  }, [initialValue]);

  const handleSave = async () => {
    try {
      const htmlContent = editorRef.current?.innerHTML || content;
      await onSave(htmlContent);
    } catch (error) {
      console.error("Error saving:", error);
    }
  };

  const handleRequestAIChanges = async () => {
    if (!aiFeedback.trim()) return;

    try {
      await onRequestAIChanges(aiFeedback);
      setAiFeedback("");
      setShowAIFeedback(false);
    } catch (error) {
      console.error("Error requesting AI changes:", error);
    }
  };

  const execCommand = (command: string, value?: string) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && e.ctrlKey) {
      e.preventDefault();
      handleSave();
    }
  };

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="bg-gray-100 border border-gray-300 rounded-t-lg p-2 flex flex-wrap gap-1">
        <button
          onClick={() => execCommand("bold")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm font-bold"
          title="Negrita"
        >
          B
        </button>
        <button
          onClick={() => execCommand("italic")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm italic"
          title="Cursiva"
        >
          I
        </button>
        <button
          onClick={() => execCommand("underline")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm underline"
          title="Subrayado"
        >
          U
        </button>
        <button
          onClick={() => execCommand("insertUnorderedList")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm"
          title="Lista no ordenada"
        >
          •
        </button>
        <button
          onClick={() => execCommand("insertOrderedList")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm"
          title="Lista ordenada"
        >
          1.
        </button>
        <button
          onClick={() => execCommand("formatBlock", "<h1>")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm font-bold"
          title="Título 1"
        >
          H1
        </button>
        <button
          onClick={() => execCommand("formatBlock", "<h2>")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm font-bold"
          title="Título 2"
        >
          H2
        </button>
        <button
          onClick={() => execCommand("formatBlock", "<h3>")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm font-bold"
          title="Título 3"
        >
          H3
        </button>
        <button
          onClick={() => execCommand("formatBlock", "<p>")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm"
          title="Párrafo"
        >
          P
        </button>
        <button
          onClick={() => execCommand("justifyLeft")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm"
          title="Alinear izquierda"
        >
          ←
        </button>
        <button
          onClick={() => execCommand("justifyCenter")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm"
          title="Centrar"
        >
          ↔
        </button>
        <button
          onClick={() => execCommand("justifyRight")}
          className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm"
          title="Alinear derecha"
        >
          →
        </button>
      </div>

      {/* Editor */}
      <div
        ref={editorRef}
        contentEditable
        dangerouslySetInnerHTML={{ __html: content }}
        onInput={(e) => setContent(e.currentTarget.innerHTML)}
        onKeyDown={handleKeyDown}
        className="min-h-[400px] p-4 border border-gray-300 rounded-b-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
        style={{
          fontFamily: "Arial, sans-serif",
          fontSize: "14px",
          lineHeight: "1.6",
        }}
      />

      {/* AI Feedback Section */}
      <div className="space-y-3">
        <button
          onClick={() => setShowAIFeedback(!showAIFeedback)}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
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
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
            />
          </svg>
          Solicitar Cambios a la IA
        </button>

        {showAIFeedback && (
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <label className="block text-sm font-medium text-purple-800 mb-2">
              Describe los cambios que quieres que la IA realice:
            </label>
            <textarea
              value={aiFeedback}
              onChange={(e) => setAiFeedback(e.target.value)}
              placeholder="Ej: Cambiar el tono a más formal, agregar más detalles sobre los hechos, modificar la estructura..."
              className="w-full h-24 p-3 border border-purple-300 rounded-lg resize-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <div className="flex gap-2 mt-3">
              <button
                onClick={handleRequestAIChanges}
                disabled={!aiFeedback.trim() || isRequestingAI}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isRequestingAI ? "Enviando..." : "Enviar Solicitud"}
              </button>
              <button
                onClick={() => {
                  setShowAIFeedback(false);
                  setAiFeedback("");
                }}
                className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
        <button
          onClick={onCancel}
          className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-colors"
        >
          Cancelar
        </button>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? "Guardando..." : "Guardar Cambios"}
        </button>
      </div>
    </div>
  );
};
