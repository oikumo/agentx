export type OmtOutcome = "succeeded" | "blocked" | "not_applicable" | "inconclusive" | "failed";

export interface OmtBlocker {
  gate: string;
  code: string;
  message: string;
  remediation?: string;
  requiresApproval: boolean;
}

export interface OmtResult<T = unknown> {
  ok: boolean;
  outcome: OmtOutcome;
  code: string;
  data?: T;
  blocker?: OmtBlocker;
  evidence: string[];
  retryable: boolean;
  stateRevision?: string;
}
