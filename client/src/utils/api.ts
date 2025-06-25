// src/api.ts
import axios from "axios";

export const API_URL = "http://localhost:8006";

export const sendFilesInitialDemand = async (formData: FormData) => {
  try {
    const response = await axios.post(`${API_URL}/api/upload-files`, formData);
    return response.data;
  } catch (error) {
    console.error("Error al generar resumen de la sentencia:", error);
    throw new Error("Hubo un error al generar el resumen de la sentencia");
  }
};
export const sendFilesSecondFormat = async (formData: FormData) => {
  try {
    const response = await axios.post(
      `${API_URL}/api/upload-files-two`,
      formData
    );
    return response.data;
  } catch (error) {
    console.error("Error al generar resumen de la sentencia:", error);
    throw new Error("Hubo un error al generar el resumen de la sentencia");
  }
};

export const getSentence = async (hash: string) => {
  try {
    const response = await axios.get(`${API_URL}/api/sentencia/${hash}`);
    return response.data;
  } catch (error) {
    console.error("Error al obtener resumen de la sentencia:", error);
    throw new Error("Hubo un error al obtener el resumen de la sentencia");
  }
};

export const uploadData = async (formData: FormData, clientId: string) => {
  try {
    const response = await axios.post(`${API_URL}/api/upload/`, formData, {
      headers: {
        "client-id": clientId,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error al enviar datos:", error);
    throw new Error("Hubo un error al enviar los datos");
  }
};

export const getCaseResults = async (caseId: string) => {
  try {
    const response = await axios.get(`${API_URL}/api/case/${caseId}/results`);
    return response.data;
  } catch (error) {
    console.error("Error al obtener resultados del caso:", error);
    throw new Error("Hubo un error al obtener los resultados del caso");
  }
};

export const getCaseStatus = async (caseId: string) => {
  try {
    const response = await axios.get(`${API_URL}/api/case/${caseId}/status`);
    return response.data;
  } catch (error) {
    console.error("Error al obtener estado del caso:", error);
    throw new Error("Hubo un error al obtener el estado del caso");
  }
};

export const updateDemand = async (caseId: string, htmlContent: string) => {
  try {
    const formData = new FormData();
    formData.append("html_content", htmlContent);

    const response = await axios.put(
      `${API_URL}/api/case/${caseId}/demand`,
      formData
    );
    return response.data;
  } catch (error) {
    console.error("Error al actualizar la demanda:", error);
    throw new Error("Hubo un error al actualizar la demanda");
  }
};

export const updateAgreement = async (caseId: string, htmlContent: string) => {
  try {
    const formData = new FormData();
    formData.append("html_content", htmlContent);

    const response = await axios.put(
      `${API_URL}/api/case/${caseId}/agreement`,
      formData
    );
    return response.data;
  } catch (error) {
    console.error("Error al actualizar el convenio:", error);
    throw new Error("Hubo un error al actualizar el convenio");
  }
};

export const requestAIChanges = async (
  caseId: string,
  documentType: "demand" | "agreement",
  userFeedback: string
) => {
  try {
    const formData = new FormData();
    formData.append("document_type", documentType);
    formData.append("user_feedback", userFeedback);

    const response = await axios.post(
      `${API_URL}/api/case/${caseId}/request-ai-changes`,
      formData
    );
    return response.data;
  } catch (error) {
    console.error("Error al solicitar cambios a la IA:", error);
    throw new Error("Hubo un error al solicitar cambios a la IA");
  }
};

export const approveCase = async (caseId: string) => {
  try {
    const response = await axios.post(`${API_URL}/api/case/${caseId}/approve`);
    return response.data;
  } catch (error) {
    console.error("Error al aprobar el caso:", error);
    throw new Error("Hubo un error al aprobar el caso");
  }
};
