"use client";

import { WORKFLOW_STEPS, WorkflowStep } from "@/lib/types";

interface WorkflowStatusProps {
  currentStage?: string;
  status?: string;
}

const STATUS_BADGE_COLORS: Record<WorkflowStep["status"], string> = {
  pending: "bg-gray-200 text-gray-500",
  active: "bg-blue-500 text-white animate-pulse",
  completed: "bg-green-500 text-white",
  rejected: "bg-red-500 text-white",
};

const STATUS_LABEL_CLASSES: Record<WorkflowStep["status"], string> = {
  active: "font-semibold text-blue-700",
  completed: "text-green-700",
  rejected: "text-red-700 line-through",
  pending: "text-gray-500",
};

function resolveStepStatus(
  step: WorkflowStep,
  currentStage: string | undefined,
  status: string | undefined
): WorkflowStep["status"] {
  if (!currentStage) return "pending";

  const currentIndex = WORKFLOW_STEPS.findIndex((s) => s.name === currentStage);
  const stepIndex = WORKFLOW_STEPS.findIndex((s) => s.name === step.name);

  if (status === "rejected" && stepIndex === currentIndex) return "rejected";
  if (stepIndex < currentIndex) return "completed";
  if (stepIndex === currentIndex) return "active";
  return "pending";
}

export default function WorkflowStatus({ currentStage, status }: WorkflowStatusProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Workflow Progress</h3>
      <div className="space-y-2">
        {WORKFLOW_STEPS.map((step, index) => {
          const stepStatus = resolveStepStatus(step, currentStage, status);
          return (
            <div key={step.name} className="flex items-center gap-2">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${STATUS_BADGE_COLORS[stepStatus]}`}
              >
                {stepStatus === "completed" ? "\u2713" : index + 1}
              </div>
              <span className={`text-sm ${STATUS_LABEL_CLASSES[stepStatus]}`}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
