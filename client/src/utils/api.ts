// src/api.ts
import axios from "axios";
export const DEV_MODE = true;
export const API_URL = DEV_MODE ? "http://localhost:8006" : "";

// Auth functions
export const signup = async (
  email: string,
  password: string,
  name?: string
) => {
  try {
    const formData = new FormData();
    formData.append("email", email);
    formData.append("password", password);
    if (name) formData.append("name", name);

    console.log(API_URL, "URL of API");

    const response = await axios.post(`${API_URL}/api/signup`, formData);
    return response.data;
  } catch (error) {
    console.error("Error al registrarse:", error);
    throw new Error("Hubo un error al registrarse");
  }
};

export const login = async (email: string, password: string) => {
  try {
    const formData = new FormData();
    formData.append("email", email);
    formData.append("password", password);

    const response = await axios.post(`${API_URL}/api/login`, formData);
    return response.data;
  } catch (error) {
    console.error("Error al iniciar sesión:", error);
    throw new Error("Hubo un error al iniciar sesión");
  }
};

export const deleteAccount = async (email: string, password: string) => {
  try {
    const formData = new FormData();
    formData.append("email", email);
    formData.append("password", password);

    const response = await axios.delete(`${API_URL}/api/delete-account`, {
      data: formData,
    });
    return response.data;
  } catch (error) {
    console.error("Error al eliminar cuenta:", error);
    throw new Error("Hubo un error al eliminar la cuenta");
  }
};

export const createWorkflow = async (
  name: string,
  description: string,
  instructions: string,
  files: File[],
  descriptions: string[],
  userEmail: string
) => {
  try {
    const formData = new FormData();
    formData.append("name", name);
    formData.append("description", description);
    formData.append("instructions", instructions);

    files.forEach((file, index) => {
      formData.append("output_examples", file);
      if (descriptions[index]) {
        formData.append("output_examples_description", descriptions[index]);
      }
    });

    const response = await axios.post(`${API_URL}/api/workflow`, formData, {
      headers: { "x-user-email": userEmail },
    });
    return response.data;
  } catch (error) {
    console.error("Error al crear workflow:", error);
    throw new Error("Hubo un error al crear el workflow");
  }
};

export const deleteWorkflow = async (workflowId: string, userEmail: string) => {
  try {
    const response = await axios.delete(
      `${API_URL}/api/workflow/${workflowId}`,
      {
        headers: { "x-user-email": userEmail },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error al eliminar workflow:", error);
    throw new Error("Hubo un error al eliminar el workflow");
  }
};

export const getWorkflows = async (userEmail: string) => {
  try {
    const response = await axios.get(`${API_URL}/api/workflows`, {
      headers: { "x-user-email": userEmail },
    });
    return response.data;
  } catch (error) {
    console.error("Error al obtener workflows:", error);
    throw new Error("Hubo un error al obtener los workflows");
  }
};

export const getWorkflow = async (workflowId: string, userEmail: string) => {
  try {
    const response = await axios.get(`${API_URL}/api/workflow/${workflowId}`, {
      headers: { "x-user-email": userEmail },
    });
    return response.data;
  } catch (error) {
    console.error("Error al obtener workflow:", error);
    throw new Error("Hubo un error al obtener el workflow");
  }
};

export const updateWorkflow = async (
  workflowId: string,
  name: string,
  description: string,
  instructions: string,
  userEmail: string
) => {
  try {
    const formData = new FormData();
    formData.append("name", name);
    formData.append("description", description);
    formData.append("instructions", instructions);

    const response = await axios.put(
      `${API_URL}/api/workflow/${workflowId}`,
      formData,
      {
        headers: { "x-user-email": userEmail },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error al actualizar workflow:", error);
    throw new Error("Hubo un error al actualizar el workflow");
  }
};

export const getWorkflowExecution = async (
  executionId: string,
  userEmail: string
) => {
  try {
    const response = await axios.get(
      `${API_URL}/api/workflow-execution/${executionId}`,
      {
        headers: { "x-user-email": userEmail },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error al obtener ejecución de workflow:", error);
    throw new Error("Hubo un error al obtener la ejecución de workflow");
  }
};

// Workflow execution
export const startWorkflow = async (
  workflowId: string,
  files: File[],
  descriptions: string[],
  userEmail: string,
  inputText?: string
) => {
  try {
    const formData = new FormData();

    formData.append("input_text", inputText || "");

    files.forEach((file, index) => {
      formData.append("input_files", file);
      if (descriptions[index]) {
        formData.append("input_descriptions", descriptions[index]);
      }
    });

    const response = await axios.post(
      `${API_URL}/api/start/${workflowId}`,
      formData,
      {
        headers: {
          "x-user-email": userEmail,
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error al iniciar workflow:", error);
    throw new Error("Hubo un error al iniciar el workflow");
  }
};

export const getWorkflowExecutionAssets = async (
  executionId: string,
  userEmail: string
) => {
  try {
    const response = await axios.get(
      `${API_URL}/api/workflow-execution/${executionId}/assets`,
      {
        headers: { "x-user-email": userEmail },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error al obtener assets de ejecución:", error);
    throw new Error("Hubo un error al obtener los assets de la ejecución");
  }
};

export const getWorkflowExecutions = async (userEmail: string) => {
  try {
    const response = await axios.get(`${API_URL}/api/workflow-executions`, {
      headers: { "x-user-email": userEmail },
    });
    return response.data;
  } catch (error) {
    console.error("Error al obtener ejecuciones:", error);
    throw new Error("Hubo un error al obtener las ejecuciones");
  }
};

// Legacy functions for backward compatibility
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

export const deleteWorkflowExecution = async (
  executionId: string,
  userEmail: string
) => {
  try {
    const response = await axios.delete(
      `${API_URL}/api/workflow-execution/${executionId}`,
      {
        headers: { "x-user-email": userEmail },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error al eliminar la ejecución:", error);
    throw new Error("Hubo un error al eliminar la ejecución");
  }
};

export const rerunWorkflowExecution = async (
  executionId: string,
  userEmail: string
) => {
  try {
    const response = await axios.post(
      `${API_URL}/api/workflow-execution/${executionId}/rerun`,
      {},
      {
        headers: { "x-user-email": userEmail },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error al re-ejecutar la ejecución:", error);
    throw new Error("Hubo un error al re-ejecutar la ejecución");
  }
};

export const convertAsset = async (
  assetId: string,
  userEmail: string,
  exportType: string
) => {
  try {
    const formData = new FormData();
    formData.append("export_type", exportType);

    const response = await axios.post(
      `${API_URL}/api/convert/asset/${assetId}`,
      formData,
      {
        headers: {
          "x-user-email": userEmail,
        },
      }
    );

    console.log(response.data, "response");
    return response.data;
  } catch (error) {
    console.error("Error al convertir el asset:", error);
    throw new Error("Hubo un error al convertir el asset");
  }
};

export const deleteAsset = async (assetId: string, userEmail: string) => {
  try {
    const response = await axios.delete(`${API_URL}/api/asset/${assetId}`, {
      headers: {
        "x-user-email": userEmail,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error al eliminar el asset:", error);
    throw new Error("Hubo un error al eliminar el asset");
  }
};

export const getSupportedExportTypes = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/convert/supported-types`);
    return response.data;
  } catch (error) {
    console.error("Error al obtener tipos de exportación:", error);
    throw new Error("Hubo un error al obtener los tipos de exportación");
  }
};

export const requestChanges = async (
  assetId: string,
  changes: string,
  userEmail: string,
  not_id: string
) => {
  const formData = new FormData();
  formData.append("changes", changes);
  formData.append("not_id", not_id);
  try {
    const response = await axios.post(
      `${API_URL}/api/request-changes/${assetId}`,
      formData,
      {
        headers: { "x-user-email": userEmail },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error al solicitar cambios a la IA:", error);
    throw new Error("Hubo un error al solicitar cambios a la IA");
  }
};
