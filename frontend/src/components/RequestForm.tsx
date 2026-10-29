"use client";

import { useState } from "react";
import { useCoAgent, useCopilotChat } from "@copilotkit/react-core";
import { Role, TextMessage } from "@copilotkit/runtime-client-gql";
import { Department, FinancialRequest } from "@/lib/types";

const DEPARTMENTS: Department[] = ["engineering", "marketing", "operations", "research", "hr"];
const PRIORITIES = ["low", "normal", "high", "urgent"];

export default function RequestForm() {
  const { appendMessage } = useCopilotChat();
  // The graph reads request fields (amount, department, ...) from state, not from chat text,
  // so the form also writes them into the agent state that is sent with the run.
  const { setState } = useCoAgent<Partial<FinancialRequest>>({ name: "approval_agent" });
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    amount: "",
    department: "engineering" as Department,
    requester: "",
    justification: "",
    priority: "normal",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const message = `Please process this financial approval request:
- Title: ${formData.title}
- Amount: $${parseFloat(formData.amount).toLocaleString()}
- Department: ${formData.department}
- Requester: ${formData.requester}
- Priority: ${formData.priority}
- Description: ${formData.description}
- Justification: ${formData.justification}`;

    setState({
      request_id: `REQ-${Date.now()}`,
      title: formData.title,
      description: formData.description,
      amount: parseFloat(formData.amount),
      department: formData.department,
      requester: formData.requester,
      justification: formData.justification,
      priority: formData.priority as FinancialRequest["priority"],
    });
    appendMessage(new TextMessage({ role: Role.User, content: message }));

    setFormData({
      title: "",
      description: "",
      amount: "",
      department: "engineering",
      requester: "",
      justification: "",
      priority: "normal",
    });
    setIsOpen(false);
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="w-full p-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        + New Approval Request
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-4 space-y-3">
      <h3 className="text-lg font-semibold text-gray-800">New Financial Request</h3>

      <input
        type="text"
        placeholder="Request Title"
        value={formData.title}
        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
        className="w-full p-2 border rounded text-sm"
        required
      />

      <div className="flex gap-2">
        <input
          type="number"
          placeholder="Amount ($)"
          value={formData.amount}
          onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
          className="flex-1 p-2 border rounded text-sm"
          min="0"
          step="0.01"
          required
        />
        <select
          value={formData.department}
          onChange={(e) => setFormData({ ...formData, department: e.target.value as Department })}
          className="flex-1 p-2 border rounded text-sm"
        >
          {DEPARTMENTS.map((dept) => (
            <option key={dept} value={dept}>
              {dept.charAt(0).toUpperCase() + dept.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <input
        type="text"
        placeholder="Your Name"
        value={formData.requester}
        onChange={(e) => setFormData({ ...formData, requester: e.target.value })}
        className="w-full p-2 border rounded text-sm"
        required
      />

      <textarea
        placeholder="Description"
        value={formData.description}
        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        className="w-full p-2 border rounded text-sm"
        rows={2}
        required
      />

      <textarea
        placeholder="Business Justification"
        value={formData.justification}
        onChange={(e) => setFormData({ ...formData, justification: e.target.value })}
        className="w-full p-2 border rounded text-sm"
        rows={2}
        required
      />

      <select
        value={formData.priority}
        onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
        className="w-full p-2 border rounded text-sm"
      >
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>
            {p.charAt(0).toUpperCase() + p.slice(1)} Priority
          </option>
        ))}
      </select>

      <div className="flex gap-2">
        <button
          type="submit"
          className="flex-1 p-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"
        >
          Submit Request
        </button>
        <button
          type="button"
          onClick={() => setIsOpen(false)}
          className="flex-1 p-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
