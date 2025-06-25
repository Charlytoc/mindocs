import { useState, useEffect } from "react";
import { FormularioDemandas } from "./components/Files/FormularioDemandas";
import { Waiter } from "./components/Waiter/Waiter";
import { Results } from "./components/Results/Results";
import { Formulario2 } from "./components/Files/Formulario2";

function App() {
  const [caseId, setCaseId] = useState<string | null>(null);
  const [processCompleted, setProcessCompleted] = useState(false);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const caseParam = urlParams.get("case");
    if (caseParam) {
      setCaseId(caseParam);
    }
  }, []);

  const handleUploadSuccess = ({ case_id }: { case_id: string }) => {
    setCaseId(case_id);
    setProcessCompleted(false);
    // Actualizar la URL con el process_id
    const url = new URL(window.location.href);
    url.searchParams.set("case", case_id);
    window.history.pushState({}, "", url.toString());
  };

  const handleFinish = () => {
    setProcessCompleted(true);
  };

  return (
    <div
      className="bg-gray-100"
      style={{ scrollBehavior: "smooth", scrollbarWidth: "none" }}
    >
      {caseId ? (
        processCompleted ? (
          <Results caseId={caseId} />
        ) : (
          <Waiter caseId={caseId} onFinish={handleFinish} />
        )
      ) : (
        <>
          <FormularioDemandas onUploadSuccess={handleUploadSuccess} />
          {/* <Formulario2 onUploadSuccess={handleUploadSuccess} /> */}
        </>
      )}
    </div>
  );
}

export default App;
