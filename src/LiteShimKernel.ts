// src/LiteShimKernel.ts
import { ChatHttpKernel } from "./ChatHttpKernel";

export interface ExecuteResult {
  "text/plain": string;
}

export class LiteShimKernel {
  private chat: ChatHttpKernel;

  constructor(chat?: ChatHttpKernel) {
    // If a ChatHttpKernel is passed, use it; otherwise create a default one
    this.chat = chat ?? new ChatHttpKernel();
  }

  async execute(code: string): Promise<ExecuteResult> {
    console.log("[LiteShimKernel] execute called with code:", code);
    const reply = await this.chat.send(code);
    console.log("[LiteShimKernel] reply to show in notebook:", reply);

    // Shape this like a Jupyter text/plain output
    return { "text/plain": reply };
  }
}
