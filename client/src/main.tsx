import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { Toaster } from "react-hot-toast";
import { BrowserRouter, Route, Routes } from "react-router";
import { WorkflowDetail } from "./routes/Workflow/page.tsx";
import { WorkflowExecutionDetail } from "./routes/Workflow/execution/page.tsx";

import App from "./App.tsx";
// import { Chat } from "./components/Chat/Chat.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Toaster />
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/workflow/:id" element={<WorkflowDetail />} />
        <Route
          path="/workflow/:id/execution/:execution_id"
          element={<WorkflowExecutionDetail />}
        />
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
