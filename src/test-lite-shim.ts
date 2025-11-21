// src/test-lite-shim.ts
import { LiteShimKernel } from "./LiteShimKernel";

(async () => {
  const k = new LiteShimKernel();
  await k.execute("Explain what this kernel is doing in one sentence.");
})();