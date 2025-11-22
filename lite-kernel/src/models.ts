// lite-kernel/src/models.ts
// Dynamically derive the list of WebLLM models from upstream WebLLM.
//
// NOTE:
// - @built-in-ai/web-llm gives you the provider function `webLLM(...)`.
// - @mlc-ai/web-llm exposes `prebuiltAppConfig.model_list`, which is the
//   authoritative list of built-in models (see WebLLM docs).

import { prebuiltAppConfig } from "@mlc-ai/web-llm";

// All available model IDs from WebLLM (runtime list)
export const WEBLLM_MODELS: string[] = prebuiltAppConfig.model_list.map(
  (record: any) => record.model_id,
);

// Preferred defaults in order of choice
const PREFERRED_DEFAULTS = [
  "Llama-3.2-3B-Instruct-q4f16_1-MLC",
  "Llama-3.1-8B-Instruct-q4f32_1-MLC",
  "Mistral-7B-Instruct-v0.3-q4f16_1-MLC",
];

// Pick the first preferred model that actually exists;
// fall back to the first model in the list as a last resort.
export const DEFAULT_WEBLLM_MODEL: string =
  PREFERRED_DEFAULTS.find((m) => WEBLLM_MODELS.includes(m)) ??
  WEBLLM_MODELS[0];

// Validation helper: check if a string is one of the known model IDs
export function isValidWebLLMModel(id: string): boolean {
  return WEBLLM_MODELS.includes(id);
}
