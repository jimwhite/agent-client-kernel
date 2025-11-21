import { JupyterFrontEnd, JupyterFrontEndPlugin } from "@jupyterlab/application";
// ❌ remove this: import { IKernelSpecs } from "@jupyterlite/kernel";

import { HttpLiteKernel } from "./kernel.js";

console.log("[lite-kernel] entrypoint loaded");

/**
 * JupyterLite / JupyterLab plugin that registers our HTTP-backed kernel.
 */
const httpChatKernelPlugin: JupyterFrontEndPlugin<void> = {
  id: "http-chat-kernel:plugin",
  autoStart: true,
  // ❌ remove `requires: [IKernelSpecs]`,
  activate: (app: JupyterFrontEnd) => {
    console.log("[http-chat-kernel] Activating plugin");

    // Grab kernelspecs from the app's serviceManager
    const anyApp = app as any;
    const kernelspecs = anyApp.serviceManager?.kernelspecs;

    if (!kernelspecs || typeof kernelspecs.register !== "function") {
      console.warn(
        "[http-chat-kernel] kernelspecs.register is not available; kernel will not be registered.",
        kernelspecs
      );
      return;
    }

    kernelspecs.register({
      id: "http-chat",
      spec: {
        name: "http-chat",
        display_name: "HTTP Chat (ACP)",
        language: "python", // purely cosmetic; syntax highlighting
        argv: [],
        resources: {}
      },
      create: (options: any) => {
        console.log("[http-chat-kernel] Creating HttpLiteKernel instance", options);
        return new HttpLiteKernel(options);
      }
    });

    console.log("[http-chat-kernel] Kernel spec 'http-chat' registered");
  }
};

const plugins: JupyterFrontEndPlugin<any>[] = [httpChatKernelPlugin];

export default plugins;

// --- manual MF shim stays the same ---
declare const window: any;

if (typeof window !== "undefined") {
  const scope = "lite-kernel";

  window._JUPYTERLAB = window._JUPYTERLAB || {};

  if (!window._JUPYTERLAB[scope]) {
    window._JUPYTERLAB[scope] = {
      get: (module: string) => {
        if (module === "./index") {
          return Promise.resolve(() => ({ default: plugins }));
        }
        return Promise.reject(new Error(`[lite-kernel] Unknown module: ${module}`));
      },
      init: () => {
        console.log("[lite-kernel] Module federation shim init()");
      }
    };

    console.log("[lite-kernel] Registered manual Module Federation shim on window._JUPYTERLAB");
  }
}
