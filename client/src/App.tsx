import { useEffect } from "react";
// import { Waiter } from "./components/Waiter/Waiter";
// import { Results } from "./components/Results/Results";
// import { Auth } from "./components/Auth/Auth";
import { WorkflowList } from "./components/Workflows/WorkflowList";
import { Navigation } from "./components/Navigation/Navigation";
import { useNavigate } from "react-router";



interface Workflow {
  id: string;
  name: string;
  description: string;
}

function App() {
  // const { isAuthenticated } = useAuthStore();
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


  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation />
      <WorkflowList onSelectWorkflow={handleWorkflowSelect} />

    </div>
  );
}

export default App;
