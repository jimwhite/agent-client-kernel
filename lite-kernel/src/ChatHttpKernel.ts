// lite-kernel/src/ChatHttpKernel.ts

export interface ChatHttpKernelOptions {
    endpoint?: string;
  }
  
  export class ChatHttpKernel {
    private endpoint: string;
  
    constructor(opts: ChatHttpKernelOptions = {}) {
      this.endpoint = opts.endpoint ?? "http://localhost:8001/chat";
      console.log("[ChatHttpKernel] Using endpoint:", this.endpoint);
    }
  
    async send(prompt: string): Promise<string> {
      console.log("[ChatHttpKernel] Sending prompt:", prompt);
  
      const resp = await fetch(this.endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      });
  
      if (!resp.ok) {
        const text = await resp.text().catch(() => "");
        console.error("[ChatHttpKernel] HTTP error", resp.status, text);
        throw new Error(`HTTP ${resp.status}: ${text || resp.statusText}`);
      }
  
      const data = (await resp.json()) as {
        reply?: string;
        error?: string;
        detail?: string;
      };
  
      if (data.error) {
        console.error("[ChatHttpKernel] LLM error:", data.error, data.detail);
        throw new Error(`LLM error: ${data.error} – ${data.detail ?? ""}`);
      }
  
      const reply = data.reply ?? "";
      console.log("[ChatHttpKernel] Got reply:", reply);
      return reply;
    }
  }
  