// src/test-chat-http.ts
import { ChatHttpKernel } from "./ChatHttpKernel";

(async () => {
  const kernel = new ChatHttpKernel({
    endpoint: "http://localhost:8000/chat",
  });

  try {
    const reply = await kernel.send("Hello from ChatHttpKernel test");
    console.log("TEST REPLY:", reply);
  } catch (err) {
    console.error("TEST ERROR:", err);
  }
})();