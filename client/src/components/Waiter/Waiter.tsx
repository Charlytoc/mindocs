export const Waiter = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4 w-full">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        {/* Loading Animation */}
        <div className="mb-6">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 bg-blue-600 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold text-gray-800 mb-3">
          Generando Documentos Iniciales
        </h2>

        {/* Description */}
        <p className="text-gray-600 mb-6 leading-relaxed">
          Estamos preparando y procesando los documentos necesarios para
          comenzar. Esto puede tomar unos momentos...
        </p>

        {/* Progress Indicators */}
        <div className="space-y-4 mb-6">
          {/* Step 1: Completed */}
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
            <span className="text-sm font-medium text-green-700">
              Archivos recibidos
            </span>
            <div className="flex items-center">
              <svg
                className="w-5 h-5 text-green-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          </div>

          {/* Step 2: In Progress */}
          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
            <span className="text-sm font-medium text-blue-700">
              Leyendo archivos
            </span>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 border-2 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
              <span className="text-xs text-blue-600">En proceso</span>
            </div>
          </div>

          {/* Step 3: Not Started */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
            <span className="text-sm font-medium text-gray-500">
              Escribiendo la demanda inicial
            </span>
            <div className="flex items-center">
              <span className="text-xs text-gray-400">Sin empezar aún</span>
            </div>
          </div>
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
