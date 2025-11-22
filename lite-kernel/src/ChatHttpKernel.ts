// lite-kernel/src/ChatHttpKernel.ts
// Browser-side chat kernel that talks directly to a local WebLLM model
// via the Vercel AI SDK + @built-in-ai/web-llm.

import { streamText } from "ai";
import { webLLM } from "@built-in-ai/web-llm";

declare const window: any;

export interface ChatHttpKernelOptions {
  /**
   * Optional model identifier for webLLM.
   * Defaults to a small, fast instruction-tuned model.
   */
  model?: string;
}

export class ChatHttpKernel {
  private modelName: string;
  private model: ReturnType<typeof webLLM>;

  constructor(opts: ChatHttpKernelOptions = {}) {
    const globalModel =
    typeof window !== "undefined" ? window.webllmModelId : undefined;

    this.modelName = opts.model ?? globalModel ?? "Llama-3.2-3B-Instruct-q4f16_1-MLC";
    this.model = webLLM(this.modelName, {
      initProgressCallback: (report) => {
        if (typeof window !== "undefined") {
          window.dispatchEvent(
            new CustomEvent("webllm:model-progress", { detail: report })
          );
        }
      },
    });

    console.log("[ChatHttpKernel] Using WebLLM model:", this.modelName);
  }

  async send(prompt: string): Promise<string> {
    const availability = await this.model.availability();
    if (availability === "unavailable") {
      throw new Error("Browser does not support WebLLM / WebGPU.");
    }
    if (availability === "downloadable" || availability === "downloading") {
      await this.model.createSessionWithProgress((report) => {
        if (typeof window !== "undefined") {
          window.dispatchEvent(
            new CustomEvent("webllm:model-progress", { detail: report })
          );
        }
      });
    }

    const result = await streamText({
      model: this.model,
      messages: [{ role: "user", content: prompt }],
    });

    let reply = "";
    for await (const chunk of result.textStream) {
      reply += chunk;
    }
    return reply;
  }
}
