import { createWorkflow } from "../../utils/api";
import { useAuthStore } from "../../infrastructure/store";
import { Modal } from "../Modal/Modal";
import { useState } from "react";

export const WorkflowForm = () => {
  const { user } = useAuthStore();
  const [isOpen, setIsOpen] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    if (!user) return;

    try {
      const response = await createWorkflow(formData, user.email);
      console.log(response);
      setIsOpen(false);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <>
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <button
          className="bg-blue-500 text-white rounded-md p-2"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? "Close" : "Create Workflow"}
        </button>
      </div>
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <div className="flex flex-col gap-4 p-4">
          <h2 className="text-2xl font-bold">Create Workflow</h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-2">
            <input
              className="w-full border-2 border-gray-300 rounded-md p-2"
              type="text"
              name="name"
              placeholder="Name"
            />
            <textarea
              className="w-full border-2 border-gray-300 rounded-md p-2"
              name="description"
              placeholder="Description"
            />
            <textarea
              className="w-full border-2 border-gray-300 rounded-md p-2"
              name="instructions"
              placeholder="Instructions"
            />
            <button
              className="bg-blue-500 text-white rounded-md p-2"
              type="submit"
            >
              Create
            </button>
          </form>
        </div>
      </Modal>
    </>
  );
};
