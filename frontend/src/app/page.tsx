"use client";

import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import ApprovalPanel from "@/components/ApprovalPanel";
import RequestForm from "@/components/RequestForm";
import WorkflowStatus from "@/components/WorkflowStatus";
import RequestHistory from "@/components/RequestHistory";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-900">
          Financial Approval System
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          AI-powered multi-stage approval workflow with human-in-the-loop review
        </p>
      </header>

      {/* Main Content */}
      <main className="flex flex-col lg:flex-row gap-4 p-4 max-w-7xl mx-auto">
        {/* Left Column - Chat */}
        <div className="flex-1 min-w-0">
          <div className="bg-white rounded-lg shadow-md h-[calc(100vh-140px)] overflow-hidden">
            <CopilotChat
              instructions="You are a financial approval assistant. Help users submit financial requests and guide them through the multi-stage approval workflow. When a request is submitted, process it through risk assessment, manager review, budget validation, finance review, and final sign-off. Explain each stage clearly and help users understand the approval status."
              labels={{
                title: "Approval Assistant",
                initial: "Submit a financial request for approval. You can use the form on the right or describe your request here.",
              }}
            />
          </div>
        </div>

        {/* Right Column - Controls */}
        <div className="w-full lg:w-80 space-y-4">
          <RequestForm />
          <WorkflowStatus />
          <RequestHistory />
        </div>
      </main>

      {/* Approval Panel - renders as modal overlay when interrupt fires */}
      <ApprovalPanel />
    </div>
  );
}
