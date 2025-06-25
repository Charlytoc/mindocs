import { useRef, useState } from "react";
import { FileInput } from "./FileInput";
import { Modal } from "../Modal/Modal";
import { sendFilesSecondFormat } from "../../utils/api";
import toast from "react-hot-toast";
import MultiSelect from "./MultiSelect";

type FormularioDemandasProps = {
  onUploadSuccess?: ({ case_id }: { case_id: string }) => void;
};

export type HashedFile = {
  name: string;
  type: string;
  hash: string;
};

export const Formulario2: React.FC<FormularioDemandasProps> = ({
  onUploadSuccess,
}) => {
  const nombreJuzgadoRef = useRef<HTMLInputElement>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [files, setFiles] = useState<FileList | null>(null);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Nuevos estados para los campos adicionales
  const [solicitante, setSolicitante] = useState("");
  const [solicitanteAdjuntos, setSolicitanteAdjuntos] =
    useState<FileList | null>(null);

  const [demandado, setDemandado] = useState("");
  const [demandadoAdjuntos, setDemandadoAdjuntos] = useState<FileList | null>(
    null
  );

  const [abogadosAdjuntos, setAbogadosAdjuntos] = useState<FileList | null>(
    null
  );

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();

    const tid = toast.loading("Enviando archivos...");
    setIsLoading(true);
    const formData = new FormData();

    // Anexos generales
    if (files) {
      for (let i = 0; i < files.length; i++) {
        formData.append("anexos", files[i]);
      }
    }

    // Solicitante/Actor
    formData.append("solicitante", solicitante);
    if (solicitanteAdjuntos) {
      for (let i = 0; i < solicitanteAdjuntos.length; i++) {
        formData.append("solicitante_adjuntos", solicitanteAdjuntos[i]);
      }
    }

    // Demandado
    formData.append("demandado", demandado);
    if (demandadoAdjuntos) {
      for (let i = 0; i < demandadoAdjuntos.length; i++) {
        formData.append("demandado_adjuntos", demandadoAdjuntos[i]);
      }
    }

    // Abogados
    if (abogadosAdjuntos) {
      for (let i = 0; i < abogadosAdjuntos.length; i++) {
        formData.append("abogados_adjuntos", abogadosAdjuntos[i]);
      }
    }

    // Otros campos
    // if (resumenDelCasoRef.current) {
    //   formData.append("resumen_del_caso", resumenDelCasoRef.current.value);
    // }
    formData.append("selected_items", selectedItems.join(","));
    formData.append("juzgado", nombreJuzgadoRef.current?.value || "");

    try {
      const response = await sendFilesSecondFormat(formData);
      setIsOpen(false);
      setIsLoading(false);
      toast.success(
        "Archivos enviados, nuestro agente IA está trabajando en ello",
        { id: tid }
      );
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
            Formulario
          </h2>
          <div>
            <input
              ref={nombreJuzgadoRef}
              className="w-full p-2 border border-gray-300 rounded-md"
              readOnly
              name="juzgado"
              placeholder="nombre_juzgado"
              value={"Juzgado Ficticio de Toluca"}
            />
          </div>

          <div>
            <label className="font-semibold">Tipo Demanda</label>
            <MultiSelect
              options={[
                { label: "Divorcio incausado", value: "divorcio_incausado" },
                { label: "Pensión alimenticia", value: "pension_alimenticia" },
                {
                  label: "Separación de bienes",
                  value: "divorcio_separacion_bienes",
                },
                { label: "Violencia familiar", value: "violencia_familiar" },
                {
                  label: "Guarda y custodia de menores",
                  value: "guarda_y_custodia_de_menores",
                },
                {
                  label: "Sucesorio intestamentario",
                  value: "sucesorio_intestamentario",
                },
                {
                  label: "Identidad de personas",
                  value: "identidad_de_personas",
                },
              ]}
              selectedValues={selectedItems}
              onChange={setSelectedItems}
              placeholder="Selecciona el tipo de demanda"
            />
          </div>

          {/* Solicitante/Actor */}
          <div>
            <label className="font-semibold">Solicitante/Actor</label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Nombre"
                value={solicitante}
                onChange={(e) => setSolicitante(e.target.value)}
                className="flex-1 p-2 border border-gray-300 rounded-md"
              />
              <FileInput
                label="Adjuntos"
                accept="image/*,.pdf,.doc,.docx,.txt"
                multiple={true}
                name="solicitante_adjuntos"
                onChange={setSolicitanteAdjuntos}
              />
            </div>
          </div>

          {/* Demandado */}
          <div>
            <label className="font-semibold">Demandado</label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Nombre"
                value={demandado}
                onChange={(e) => setDemandado(e.target.value)}
                className="flex-1 p-2 border border-gray-300 rounded-md"
              />
              <FileInput
                label="Adjuntos"
                accept="image/*,.pdf,.doc,.docx,.txt"
                multiple={true}
                name="demandado_adjuntos"
                onChange={setDemandadoAdjuntos}
              />
            </div>
          </div>

          {/* Abogado(s) */}
          <div>
            <label className="font-semibold">Abogado(s)</label>
            <FileInput
              label="Adjuntos"
              accept="image/*,.pdf,.doc,.docx,.txt"
              multiple={true}
              name="abogados_adjuntos"
              onChange={setAbogadosAdjuntos}
            />
          </div>

          {/* Anexos */}
          <div>
            <label className="font-semibold">Anexos</label>
            <FileInput
              label="Adjuntos"
              accept="image/*,.pdf,.doc,.docx,.txt"
              multiple={true}
              name="anexos"
              onChange={setFiles}
            />
          </div>

          {/* Resumen del caso (opcional) */}
          {/* <textarea
            ref={resumenDelCasoRef}
            name="resumen_del_caso"
            placeholder="Resumen del caso: Explicar brevemente el caso, los hechos, los demandados, los demandantes, etc."
            className="w-full h-40 p-2 border border-gray-300 rounded-md"
          ></textarea> */}

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
