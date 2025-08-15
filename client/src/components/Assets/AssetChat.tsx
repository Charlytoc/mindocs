import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { requestChanges } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import { toast } from "react-hot-toast";
import { generateUniqueID } from "../../utils/lib";
import socket from "../../infrastructure/socket";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
  status?: "sending" | "sent" | "error";
}

interface AssetChatProps {
  asset: {
    id: string;
    name: string;
  };
  onFinish: () => void;
  onClose: () => void;
}

export const AssetChat = ({ asset, onFinish, onClose }: AssetChatProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      text: `¡Hola! Soy tu asistente IA. ¿Qué cambios te gustaría que haga en "${asset.name}"?`,
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuthStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [not_id, setNotId] = useState<string | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (not_id) {
      socket.connect();
      socket.on(`notification_${not_id}`, (data) => {
        console.log(data);
        if (data.status === "DONE") {
          setMessages((prev) => [
            ...prev,
            {
              id: `bot-${Date.now()}`,
              text: "¡Perfecto! He realizado los cambios que solicitaste. El archivo ha sido actualizado.",
              sender: "bot",
              timestamp: new Date(),
            },
          ]);
          toast.success("Cambios realizados correctamente");
          setTimeout(() => {
            onFinish();
          }, 2000);
        }
      });
    }
    return () => {
      if (not_id) {
        socket.off(`notification_${not_id}`);
        socket.disconnect();
      }
    };
  }, [not_id, onFinish]);

  const handleSendMessage = async () => {
    if (!inputText.trim() || !user?.email) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      text: inputText.trim(),
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);

    // Add loading message
    const loadingMessage: Message = {
      id: `loading-${Date.now()}`,
      text: "Procesando tu solicitud...",
      sender: "bot",
      timestamp: new Date(),
      status: "sending",
    };

    setMessages((prev) => [...prev, loadingMessage]);

    try {
      const _not_id = generateUniqueID("not_");
      await requestChanges(asset.id, inputText.trim(), user.email, _not_id);
      setNotId(_not_id);

      // Update loading message
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingMessage.id
            ? {
                ...msg,
                text: "He recibido tu solicitud y estoy trabajando en los cambios. Te notificaré cuando esté listo.",
                status: "sent",
              }
            : msg
        )
      );
    } catch (error) {
      console.error("Error requesting changes:", error);
      toast.error("Error al solicitar cambios");

      // Update loading message to error
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingMessage.id
            ? {
                ...msg,
                text: "Lo siento, hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo.",
                status: "error",
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bot className="w-6 h-6" />
            <div>
              <h3 className="font-semibold">Asistente IA</h3>
              <p className="text-blue-100 text-sm">
                Solicita cambios en tu archivo
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-blue-100 hover:text-white transition-colors"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                message.sender === "user"
                  ? "bg-blue-600 text-white rounded-br-md"
                  : "bg-white text-gray-800 rounded-bl-md shadow-sm border border-gray-200"
              }`}
            >
              <div className="flex items-start gap-2">
                {message.sender === "bot" && (
                  <Bot
                    className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
                      message.status === "sending"
                        ? "text-blue-500"
                        : message.status === "error"
                        ? "text-red-500"
                        : "text-blue-600"
                    }`}
                  />
                )}
                <div className="flex-1">
                  <p className="text-sm leading-relaxed">{message.text}</p>
                  {message.status === "sending" && (
                    <div className="flex items-center gap-2 mt-2">
                      <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                      <span className="text-xs text-blue-500">
                        Procesando...
                      </span>
                    </div>
                  )}
                </div>
                {message.sender === "user" && (
                  <User className="w-5 h-5 mt-0.5 flex-shrink-0 text-blue-100" />
                )}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-gray-200">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyUp={handleKeyPress}
          placeholder="Describe los cambios que deseas realizar..."
          className="flex-1 resize-none border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all w-full"
          rows={2}
          disabled={isLoading}
        />

        <button
          onClick={handleSendMessage}
          disabled={!inputText.trim() || isLoading}
          className="bg-blue-600 text-white px-4 py-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2 mt-2"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Presiona Enter para enviar, Shift+Enter para nueva línea
        </p>
      </div>
    </div>
  );
};
