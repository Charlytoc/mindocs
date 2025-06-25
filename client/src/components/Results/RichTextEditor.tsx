import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import TextAlign from "@tiptap/extension-text-align";

type RichTextEditorProps = {
  initialValue: string;
  onSave: (content: string) => Promise<void>;
  onCancel: () => void;
  onRequestAIChanges: (feedback: string) => Promise<void>;
  isSaving?: boolean;
  isRequestingAI?: boolean;
};
export const RichTextEditor = ({
  initialValue,
  onSave,
  ...props
}: RichTextEditorProps) => {
  const editor = useEditor({
    extensions: [
      StarterKit,
      TextAlign.configure({
        types: ["heading", "paragraph"],
      }),
    ],
    content: initialValue,
  });

  const handleSave = () => {
    onSave(editor?.getHTML() || "");
  };

  return (
    <div className=" max-w-[816px] mx-auto bg-white rounded-lg shadow-xl">
      <div className="toolbar flex flex-wrap gap-1 mb-4 bg-gray-100 border border-gray-300 rounded-t-lg p-2 justify-center">
        <button
          className={`px-2 py-1 rounded font-bold border ${
            editor?.isActive("bold")
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800 hover:bg-blue-100"
          } `}
          onClick={() => editor?.chain().focus().toggleBold().run()}
          title="Negrita"
        >
          B
        </button>
        <button
          className={`px-2 py-1 rounded font-bold border italic ${
            editor?.isActive("italic")
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800 hover:bg-blue-100"
          } `}
          onClick={() => editor?.chain().focus().toggleItalic().run()}
          title="Cursiva"
        >
          I
        </button>
        <button
          className={`px-2 py-1 rounded border ${
            editor?.isActive("bulletList")
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800 hover:bg-blue-100"
          } `}
          onClick={() => editor?.chain().focus().toggleBulletList().run()}
          title="Lista no ordenada"
        >
          •
        </button>
        <button
          className={`px-2 py-1 rounded border ${
            editor?.isActive("orderedList")
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800 hover:bg-blue-100"
          } `}
          onClick={() => editor?.chain().focus().toggleOrderedList().run()}
          title="Lista ordenada"
        >
          1.
        </button>
        <button
          className={`px-2 py-1 rounded border ${
            editor?.isActive({ textAlign: "left" })
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800 hover:bg-blue-100"
          } `}
          onClick={() => editor?.chain().focus().setTextAlign("left").run()}
          title="Alinear izquierda"
        >
          ←
        </button>
        <button
          className={`px-2 py-1 rounded border ${
            editor?.isActive({ textAlign: "center" })
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800 hover:bg-blue-100"
          } `}
          onClick={() => editor?.chain().focus().setTextAlign("center").run()}
          title="Centrar"
        >
          ↔
        </button>
        <button
          className={`px-2 py-1 rounded border ${
            editor?.isActive({ textAlign: "right" })
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800 hover:bg-blue-100"
          } `}
          onClick={() => editor?.chain().focus().setTextAlign("right").run()}
          title="Alinear derecha"
        >
          →
        </button>
        <button
          className={`px-2 py-1 rounded border ${
            editor?.isActive("heading", { level: 1 })
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800 hover:bg-blue-100"
          } `}
          onClick={() =>
            editor?.chain().focus().toggleHeading({ level: 1 }).run()
          }
          title="Título 1"
        >
          H1
        </button>
        <button
          className={`px-2 py-1 rounded border ${
            editor?.isActive("heading", { level: 2 })
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800 hover:bg-blue-100"
          } `}
          onClick={() =>
            editor?.chain().focus().toggleHeading({ level: 2 }).run()
          }
          title="Título 2"
        >
          H2
        </button>
      </div>

      <EditorContent
        editor={editor}
        className="prose max-w-none min-h-[300px] p-4 rounded"
      />
      <div className="flex justify-end p-4">
        <button
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed "
          disabled={props.isSaving}
          onClick={handleSave}
        >
          {props.isSaving ? "Guardando..." : "Guardar"}
        </button>
      </div>
    </div>
  );
};
