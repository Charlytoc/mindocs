import { useRef, useState } from "react";
import { FileInput } from "./FileInput";
import { Modal } from "../Modal/Modal";
import { sendFilesInitialDemand } from "../../utils/api";
import toast from "react-hot-toast";

type FileUploaderProps = {
  onUploadSuccess?: ({ case_id }: { case_id: string }) => void;
};

export type HashedFile = {
  name: string;
  type: string;
  hash: string;
};

export const FileUploader: React.FC<FileUploaderProps> = ({
  onUploadSuccess,
}) => {
  const resumenDelCasoRef = useRef<HTMLTextAreaElement>(null);
  // const clientId = useStore((state) => state.clientId);
  const [isOpen, setIsOpen] = useState(false);
  const [files, setFiles] = useState<FileList | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();

    const tid = toast.loading("Enviando archivos...");
    setIsLoading(true);
    const formData = new FormData();

    if (files) {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        formData.append("files", file);
      }
    }

    try {
      if (resumenDelCasoRef.current) {
        formData.append("resumen_del_caso", resumenDelCasoRef.current.value);
      }
      const response = await sendFilesInitialDemand(formData);
      setIsOpen(false);
      setIsLoading(false);
      toast.success(
        "Archivos enviados, nuestro agente IA está trabajando en ello",
        { id: tid }
      );
      console.log(response.case_id, "process_id");
      if (onUploadSuccess)
        onUploadSuccess({
          case_id: response.case_id,
        });
    } catch (error) {
      console.error("Error al enviar datos:", error);
      toast.error("Error al enviar los datos, estamos trabajando en ello.", {
        id: tid,
      });
      setIsLoading(false);
    }
  };

  return (
    <>
      <button
        title="Subir archivos"
        onClick={() => setIsOpen(true)}
        className="button-edomex px-2 py-1 rounded-md"
      >
        +
      </button>
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <form
          onSubmit={(e) => e.preventDefault()}
          className="max-w-lg p-6 rounded-lg flex flex-col gap-4"
        >
          <h2 className="text-3xl font-bold mb-6 text-gray-800 text-center">
            Subir Archivos
          </h2>

          <FileInput
            label="Archivos (imágenes y documentos)"
            accept="image/*,.pdf,.doc,.docx,.txt"
            multiple={true}
            name="files"
            onChange={setFiles}
          />

          <textarea
            ref={resumenDelCasoRef}
            name="resumen_del_caso"
            placeholder="Resumen del caso: Explicar brevemente el caso, los hechos, los demandados, los demandantes, etc."
            className="w-full h-40 p-2 border border-gray-300 rounded-md"
          ></textarea>

          <button
            onClick={handleSubmit}
            type="submit"
            disabled={isLoading}
            className="w-full py-2 px-4 button-edomex text-white font-semibold rounded-lg shadow-md cursor-pointer disabled:opacity-50"
          >
            {isLoading ? "Enviando archivos..." : "Listo"}
          </button>
        </form>
      </Modal>
    </>
  );
};
