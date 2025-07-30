import { useEffect, useRef, useState } from "react";
import socket from "../../infrastructure/socket";
import { getWorkflowExecutionAssets } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";

type WaiterProps = {
  executionId: string;
  onFinish: () => void;
};

export type Asset = {
  id: string;
  name: string;
  description: string;
  content: string;
  extracted_text: string;
};

export const Waiter = ({ executionId, onFinish }: WaiterProps) => {
  const logsContainerRef = useRef<HTMLDivElement>(null);
  const [logs, setLogs] = useState<string[]>([
    "Archivos recibidos",
    "Leyendo archivos",
  ]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const { user } = useAuthStore();

  // // Function to check execution status
  const checkExecutionStatus = async () => {
    if (!user) return false;

    try {
      const assetsData = await getWorkflowExecutionAssets(
        executionId,
        user.email
      );
      console.log("Execution assets:", assetsData);
      setAssets(assetsData.uploaded || []);
      // Check if there are generated assets (AI has processed the files)
      // if (assetsData.generated && assetsData.generated.length > 0) {
      //   console.log("Execution is ready, calling onFinish");
      //   onFinish();
      //   return true;
      // }
      return false;
    } catch (error) {
      console.error("Error checking execution status:", error);
      return false;
    }
  };

  useEffect(() => {
    // Check execution status immediately when component mounts or executionId changes
    checkExecutionStatus();

    socket.connect();

    socket.on("connect", () => {
      console.log("connected to socket server");
    });
    socket.on("disconnect", () => {
      console.log("disconnected from socket server");
    });

    socket.on(`workflow_update`, (data: any) => {
      console.log("workflow updated", data);
      if (data.log) {
        setLogs((prevLogs) => [...prevLogs, data.log]);
      }
      if (data.status === "DONE") {
        onFinish();
      }
    });

    socket.emit("join_workflow", { workflow_id: executionId });
    return () => {
      socket.off(`workflow_update`);
      socket.off("connect");
      socket.off("disconnect");
      socket.disconnect();
    };
  }, [executionId]);

  useEffect(() => {
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTo({
        top: logsContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [logs]);

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4 w-full">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        {/* Loading Animation */}

        <div className="flex flex-row items-center justify-center gap-2 border border-gray-200 rounded-lg p-2 mb-6 F">
          <h4 className="text-md font-bold text-gray-800 mb-3 flex items-center justify-center">
            Procesando Documentos
          </h4>

          <div className="">
            <div className="relative">
              <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
            </div>
          </div>
        </div>

        {/* Progress Indicators */}
        <div
          className="space-y-1 mb-6 max-h-96 overflow-y-auto bg-gray-50 rounded-lg border border-gray-200 p-1"
          ref={logsContainerRef}
          style={{ scrollbarWidth: "none" }}
        >
          {logs.map((log, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-1 text-left text-sm "
            >
              <span className="text-sm font-medium text-gray-500">{log}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
