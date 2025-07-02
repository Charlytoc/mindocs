import { useRef, useState } from "react";
import { FileInput } from "./FileInput";
import { Modal } from "../Modal/Modal";
import { sendFilesSecondFormat } from "../../utils/api";
import toast from "react-hot-toast";

type FormularioDemandasProps = {
  onUploadSuccess?: ({ case_id }: { case_id: string }) => void;
};

export const Formulario: React.FC<FormularioDemandasProps> = ({
  onUploadSuccess,
}) => {
  const nombreJuzgadoRef = useRef<HTMLInputElement>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [solicitanteAdjuntos, setSolicitanteAdjuntos] =
    useState<FileList | null>(null);
  const [haveChildren, setHaveChildren] = useState(false);
  const [propuestaConvenio, setPropuestaConvenio] = useState(false);
  const [demandadoAdjuntos, setDemandadoAdjuntos] = useState<FileList | null>(
    null
  );
  const [otrosAnexos, setOtrosAnexos] = useState<FileList | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const formData = new FormData(form);

    const tid = toast.loading("Enviando archivos...");
    setIsLoading(true);

    if (solicitanteAdjuntos) {
      for (let i = 0; i < solicitanteAdjuntos.length; i++) {
        formData.append("solicitante_adjuntos", solicitanteAdjuntos[i]);
      }
    }

    if (demandadoAdjuntos) {
      for (let i = 0; i < demandadoAdjuntos.length; i++) {
        formData.append("demandado_adjuntos", demandadoAdjuntos[i]);
      }
    }

    if (otrosAnexos) {
      for (let i = 0; i < otrosAnexos.length; i++) {
        formData.append("otros_anexos", otrosAnexos[i]);
      }
    }

    try {
      console.log(formData, "formData a enviar");

      for (let pair of formData.entries()) {
        console.log(pair[0], pair[1]);
      }

      const response = await sendFilesSecondFormat(formData);
      setIsOpen(false);
      setIsLoading(false);
      toast.success(
        "Archivos enviados, nuestro agente IA está trabajando en ello",
        { id: tid }
      );
      if (onUploadSuccess) onUploadSuccess({ case_id: response.case_id });
    } catch (error) {
      console.error("Error al enviar datos:", error);
      toast.error("Error al enviar los datos, estamos trabajando en ello.", {
        id: tid,
      });
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setSolicitanteAdjuntos(null);
    setDemandadoAdjuntos(null);
    setOtrosAnexos(null);
    setHaveChildren(false);
    setPropuestaConvenio(false);
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
          onSubmit={handleSubmit}
          className="max-w-lg p-6 rounded-lg flex flex-col gap-4"
        >
          <h2 className="text-3xl font-bold mb-6 text-gray-800 text-center">
            Formulario
          </h2>
          <div>
            <input
              ref={nombreJuzgadoRef}
              className="w-full p-2 border border-gray-300 rounded-md"
              readOnly
              name="juzgado"
              value={"Juzgado Ficticio Familiar de Toluca"}
            />
          </div>
          <div>
            <FileInput
              label="Acta de Matrimonio"
              accept="image/*,.pdf,.doc,.docx"
              multiple={false}
              name="acta_de_matrimonio"
              onChange={setSolicitanteAdjuntos}
              required
            />
          </div>

          <div>
            <FileInput
              label="Solicitante (Acta, INE)"
              accept="image/*,.pdf,.doc,.docx"
              multiple={false}
              name="solicitante_adjuntos"
              onChange={setSolicitanteAdjuntos}
              required
            />
          </div>

          <div className="flex flex-row gap-2 items-center">
            <label className="font-semibold">Hijos</label>
            <div className="flex gap-2">
              <input
                onClick={() => setHaveChildren(true)}
                type="radio"
                name="hijos"
                value="si"
              />
              <label>Si</label>
              <input
                onClick={() => setHaveChildren(false)}
                type="radio"
                name="hijos"
                value="no"
              />
              <label>No</label>
            </div>
          </div>

          {haveChildren && (
            <div>
              <label className="font-semibold">Hijos</label>
              <FileInput
                label="Hijos"
                accept="image/*,.pdf,.doc,.docx,.txt"
                multiple={true}
                name="hijos_files"
                onChange={setSolicitanteAdjuntos}
              />
            </div>
          )}

          <div className="flex flex-row gap-2 items-center">
            <label className="font-semibold">Propuesta de Convenio</label>
            <div className="flex gap-2">
              <input
                onClick={() => setPropuestaConvenio(true)}
                type="radio"
                name="propuesta_convenio"
                value="si"
              />
              <label>Si</label>
              <input
                onClick={() => setPropuestaConvenio(false)}
                type="radio"
                name="propuesta_convenio"
                value="no"
              />
              <label>No</label>
            </div>
          </div>

          {propuestaConvenio && (
            <div>
              <FileInput
                label="Convenio"
                accept="image/*,.pdf,.doc,.docx"
                multiple={false}
                name="convenio"
                onChange={setDemandadoAdjuntos}
              />
            </div>
          )}

          <div>
            <label className="font-semibold">Otros Anexos</label>
            <div className="flex gap-2">
              <FileInput
                label="Anexos"
                accept="image/*,.pdf,.doc,.docx"
                multiple={true}
                name="otros_anexos"
                onChange={setOtrosAnexos}
              />
            </div>
          </div>

          <div className="flex justify-between">
            <button
              type="button"
              onClick={handleClear}
              className="py-2 px-4 button-edomex text-white font-semibold rounded-lg"
            >
              Limpiar
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="py-2 px-4 button-edomex text-white font-semibold rounded-lg shadow-md cursor-pointer disabled:opacity-50"
            >
              {isLoading ? "Enviando archivos..." : "Enviar"}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
};
