// lite-kernel/src/ChatHttpKernel.ts
// Browser-side chat kernel that talks directly to a local WebLLM model
// via the Vercel AI SDK + @built-in-ai/web-llm.

import { streamText } from "ai";
import { webLLM } from "@built-in-ai/web-llm";

export interface ChatHttpKernelOptions {
  /**
   * Optional model identifier for webLLM.
   * Defaults to a small, fast instruction-tuned model.
   */
  model?: string;
}

export class ChatHttpKernel {
  private modelName: string;

  constructor(opts: ChatHttpKernelOptions = {}) {
    this.modelName = opts.model ?? "Llama-3.2-3B-Instruct-q4f16_1-MLC";
    console.log("[ChatHttpKernel] Using WebLLM model:", this.modelName);
  }

  async send(prompt: string): Promise<string> {
    console.log("[ChatHttpKernel] Sending prompt to WebLLM:", prompt);

    const result = await streamText({
      model: webLLM(this.modelName),
      messages: [{ role: "user", content: prompt }],
    });

    let reply = "";
    for await (const chunk of result.textStream) {
      reply += chunk;
    }

    console.log("[ChatHttpKernel] Got reply from WebLLM:", reply);
    return reply;
  }
}
