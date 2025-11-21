// src/browser-demo.ts
import { ChatHttpKernel } from "./ChatHttpKernel";
import { LiteShimKernel } from "./LiteShimKernel";

const chatKernel = new ChatHttpKernel({
  endpoint: "http://localhost:8000/chat",
});

const liteKernel = new LiteShimKernel(chatKernel);

// Expose a simple function on window so HTML can call it
// (type `any` to avoid needing DOM types wired up perfectly)
declare const window: any;

window.liteKernelExecute = async (code: string) => {
  const result = await liteKernel.execute(code);
  return result;
};
