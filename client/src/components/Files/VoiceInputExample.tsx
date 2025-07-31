import React, { useState } from "react";
import { VoiceInput } from "./VoiceInput";

interface FormData {
  name: string;
  description: string;
  audioRecording?: Blob;
  audioUrl?: string;
}

export const VoiceInputExample: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    name: "",
    description: "",
  });

  const handleAudioRecorded = (audioBlob: Blob, audioUrl: string) => {
    setFormData((prev) => ({
      ...prev,
      audioRecording: audioBlob,
      audioUrl: audioUrl,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const submitData = new FormData();
    submitData.append("name", formData.name);
    submitData.append("description", formData.description);

    if (formData.audioRecording) {
      submitData.append("audio", formData.audioRecording, "recording.webm");
    }

    // Aquí puedes enviar los datos al servidor
    console.log("Datos del formulario:", formData);
    console.log("FormData para enviar:", submitData);

    // Ejemplo de cómo enviar al servidor:
    // const response = await fetch('/api/submit-form', {
    //   method: 'POST',
    //   body: submitData
    // });
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center">
        Formulario con Grabación de Voz
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="name"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Nombre:
          </label>
          <input
            type="text"
            id="name"
            value={formData.name}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, name: e.target.value }))
            }
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Descripción:
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, description: e.target.value }))
            }
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Grabación de Voz (Opcional):
          </label>
          <VoiceInput onAudioRecorded={handleAudioRecorded} />
        </div>

        <div className="flex gap-2 pt-4">
          <button
            type="submit"
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Enviar Formulario
          </button>

          <button
            type="button"
            onClick={() => setFormData({ name: "", description: "" })}
            className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            Limpiar
          </button>
        </div>
      </form>

      {formData.audioUrl && (
        <div className="mt-4 p-4 bg-gray-50 rounded-md">
          <h3 className="text-sm font-medium text-gray-700 mb-2">
            Audio grabado:
          </h3>
          <audio controls src={formData.audioUrl} className="w-full" />
        </div>
      )}
    </div>
  );
};
