"use client";

import { ApprovalResult } from "@/lib/types";

interface RequestHistoryProps {
  requests?: ApprovalResult[];
}

const statusColors = {
  pending: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
  needs_review: "bg-blue-100 text-blue-800",
};

export default function RequestHistory({ requests = [] }: RequestHistoryProps) {
  if (requests.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Request History</h3>
        <p className="text-sm text-gray-400 italic">No requests yet. Submit one to get started.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Request History</h3>
      <div className="space-y-2">
        {requests.map((req) => (
          <div key={req.request_id} className="border rounded p-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-800">{req.request_id}</span>
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  statusColors[req.status] || statusColors.pending
                }`}
              >
                {req.status}
              </span>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Risk: {req.risk_level} | Approvals: {req.total_approvals}/{req.decisions.length}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
