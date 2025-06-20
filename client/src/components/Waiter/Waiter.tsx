import { useEffect, useState } from "react";
import socket from "../../infrastructure/socket";
import { getCaseStatus } from "../../utils/api";

type WaiterProps = {
  caseId: string;
  onFinish: () => void;
};

export const Waiter = ({ caseId, onFinish }: WaiterProps) => {
  const [logs, setLogs] = useState<string[]>([
    "Archivos recibidos",
    "Leyendo archivos",
  ]);

  // Function to check case status
  const checkCaseStatus = async () => {
    try {
      const statusData = await getCaseStatus(caseId);
      console.log("Case status:", statusData);

      if (statusData.has_demands && statusData.has_agreements) {
        console.log("Case is ready, calling onFinish");
        onFinish();
        return true;
      }
      return false;
    } catch (error) {
      console.error("Error checking case status:", error);
      return false;
    }
  };

  useEffect(() => {
    // Check case status immediately when component mounts or caseId changes
    checkCaseStatus();

    socket.connect();

    socket.on("connect", () => {
      console.log("connected to socket server");
    });
    socket.on("disconnect", () => {
      console.log("disconnected from socket server");
    });

    socket.on(`case_update`, (data: any) => {
      console.log("case updated", data);
      if (data.log) {
        setLogs((prevLogs) => [...prevLogs, data.log]);
      }
      if (data.status === "COMPLETED") {
        onFinish();
      }
    });

    socket.emit("join_case", { case_id: caseId });
    return () => {
      socket.off(`case_update`);
      socket.off("connect");
      socket.off("disconnect");
      socket.disconnect();
    };
  }, [caseId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4 w-full">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        {/* Loading Animation */}

        <h2 className="text-2xl font-bold text-gray-800 mb-3 flex items-center justify-center">
          Generando Documentos Iniciales
        </h2>

        <div className="mb-6 ml-3">
          <div className="relative">
            <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-5 h-5 bg-blue-600 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">
            ID del caso:{" "}
            <span className="font-mono text-gray-800">{caseId}</span>
          </p>
        </div> */}

        {/* Progress Indicators */}
        <div className="space-y-1 mb-6 max-h-96 overflow-y-auto bg-gray-50 rounded-lg border border-gray-200 p-1">
          {logs.map((log, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-1 text-left text-sm "
            >
              <span className="text-sm font-medium text-gray-500">{log}</span>
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-xs text-blue-700">
            💡 Tip: Mientras esperas, puedes revisar los archivos que has subido
            para asegurarte de que todo esté correcto.
          </p>
        </div>
      </div>
    </div>
  );
};
