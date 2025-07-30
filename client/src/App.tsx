import { useState, useEffect } from "react";
// import { Waiter } from "./components/Waiter/Waiter";
// import { Results } from "./components/Results/Results";
import { Auth } from "./components/Auth/Auth";
import { WorkflowList } from "./components/Workflows/WorkflowList";
import { WorkflowUpload } from "./components/Workflows/WorkflowUpload";
import { Navigation } from "./components/Navigation/Navigation";
import { useAuthStore } from "./infrastructure/store";
import { useNavigate } from "react-router";
import { WorkflowForm } from "./components/Workflows/WorkflowForm";

type AppState =
  | "auth"
  | "workflow-list"
  | "workflow-upload"
  | "processing"
  | "results";

interface Workflow {
  id: string;
  name: string;
  description: string;
}

function App() {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    // Check URL parameters for legacy support
    const urlParams = new URLSearchParams(window.location.search);

    const executionParam = urlParams.get("execution");

    if (executionParam) {
      // setExecutionId(executionParam);
      // setProcessCompleted(false);
      navigate(`/workflow/${executionParam}`);
    }
  }, []);

  // useEffect(() => {
  //   if (!isAuthenticated) {
  //     navigate("/");
  //   }
  // }, [isAuthenticated]);

  const handleWorkflowSelect = (workflow: Workflow) => {
    navigate(`/workflow/${workflow.id}`);
  };

  const handleUploadSuccess = ({ execution_id }: { execution_id: string }) => {
    navigate(`/workflow/${execution_id}`);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation />
      <WorkflowList onSelectWorkflow={handleWorkflowSelect} />
      <WorkflowForm />
      {/* <WorkflowUpload
        workflow={{
          id: "1",
          name: "Workflow 1",
          description: "Workflow 1 description",
        }}
        onUploadSuccess={handleUploadSuccess}
        onBack={() => {}}
      /> */}
    </div>
  );
}

export default App;
