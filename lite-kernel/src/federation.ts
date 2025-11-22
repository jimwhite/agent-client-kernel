// lite-kernel/src/federation.ts
// Module Federation container for JupyterLite

import { streamText } from "ai";
import { webLLM } from "@built-in-ai/web-llm";
import { WEBLLM_MODELS, DEFAULT_WEBLLM_MODEL } from "./models.js";

declare const window: any;

console.log("[lite-kernel/federation] Setting up Module Federation container");

const scope = "lite-kernel";
let sharedScope: any = null;

// Helper to get a module from the shared scope
async function importShared(pkg: string): Promise<any> {
  if (!sharedScope) {
    // Fallback to global webpack share scope if available
    // @ts-ignore
    if (window.__webpack_share_scopes__ && window.__webpack_share_scopes__.default) {
      console.warn(`[lite-kernel] Using global __webpack_share_scopes__.default for ${pkg}`);
      // @ts-ignore
      sharedScope = window.__webpack_share_scopes__.default;
    } else {
      throw new Error(`[lite-kernel] Shared scope not initialized when requesting ${pkg}`);
    }
  }

  const versions = sharedScope[pkg];
  if (!versions) {
    throw new Error(`[lite-kernel] Shared module ${pkg} not found in shared scope. Available: ${Object.keys(sharedScope)}`);
  }

  const versionKeys = Object.keys(versions);
  if (versionKeys.length === 0) {
    throw new Error(`[lite-kernel] No versions available for ${pkg}`);
  }

  // Pick the first available version
  const version = versions[versionKeys[0]];
  const factory = version?.get;

  if (typeof factory !== "function") {
    throw new Error(`[lite-kernel] Module ${pkg} has no factory function`);
  }

  // Factory might return a Promise or the module directly
  let result = factory();

  // If it's a promise, await it
  if (result && typeof result.then === 'function') {
    result = await result;
  }

  // If result is a function (Webpack module wrapper), call it to get the actual exports
  if (typeof result === 'function') {
    result = result();
  }

  console.log(`[lite-kernel] Loaded ${pkg}:`, result);
  return result;
}

// Module Federation container API
const container = {
  init: (scope: any) => {
    console.log("[lite-kernel/federation] init() called, storing shared scope");
    sharedScope = scope;
    return Promise.resolve();
  },

  get: async (module: string) => {
    console.log("[lite-kernel/federation] get() called for module:", module);
    console.log("[lite-kernel/federation] This means JupyterLite is requesting our plugin!");

    // JupyterLite may request either "./index" or "./extension"
    if (module === "./index" || module === "./extension") {
      // Lazy-load our plugin module, which will pull from shared scope
      return async () => {
        console.log("[lite-kernel/federation] ===== LOADING PLUGIN MODULE =====");
        console.log("[lite-kernel/federation] Loading plugins from shared scope...");

        // Import JupyterLab/JupyterLite modules from shared scope
        const { BaseKernel, IKernelSpecs } = await importShared('@jupyterlite/kernel');
        const { Widget } = await importShared('@lumino/widgets');

        const { ReactWidget } = await importShared('@jupyterlab/apputils');
        const React = await importShared('react');
        const { HTMLSelect } = await importShared('@jupyterlab/ui-components');


        console.log("[lite-kernel/federation] Got BaseKernel from shared scope:", BaseKernel);

        // Define WebLLM-backed Chat kernel inline (browser-only, no HTTP)
        class ChatHttpKernel {
          private modelName!: string;
          private model!: ReturnType<typeof webLLM>;
          private readonly initialModelOverride?: string;

          constructor(opts: any = {}) {
            this.initialModelOverride = opts.model;
            this.ensureModelUpToDate();
            console.log("[ChatHttpKernel] Using WebLLM model:", this.modelName);
          }

          /**
           * Ensure that this.model / this.modelName match the currently-selected model.
           * This lets users change the dropdown without needing to reload the page.
           */
          private ensureModelUpToDate() {
            const globalModel =
              typeof window !== "undefined" ? window.webllmModelId : undefined;

            const targetName =
              this.initialModelOverride ?? globalModel ?? DEFAULT_WEBLLM_MODEL;

            if (this.model && this.modelName === targetName) {
              return;
            }

            this.modelName = targetName;
            this.model = webLLM(this.modelName, {
              initProgressCallback: (report) => {
                if (typeof window !== "undefined") {
                  window.dispatchEvent(
                    new CustomEvent("webllm:model-progress", { detail: report })
                  );
                }
              },
            });
          }

          async send(prompt: string): Promise<string> {
            // Pick up any model change from the toolbar before each request
            this.ensureModelUpToDate();
            console.log(
              "[ChatHttpKernel] Sending prompt to WebLLM:",
              prompt,
              "using model:",
              this.modelName
            );

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

            console.log("[ChatHttpKernel] Got reply from WebLLM:", reply);
            return reply;
          }
        }

        // Define HttpLiteKernel extending BaseKernel
        class HttpLiteKernel extends BaseKernel {
          private chat: ChatHttpKernel;

          constructor(options: any) {
            super(options);
            const model = options.model;
            this.chat = new ChatHttpKernel({ model });
          }

          async executeRequest(content: any): Promise<any> {
            const code = String(content.code ?? "");
            try {
              const reply = await this.chat.send(code);
              // @ts-ignore
              this.publishExecuteResult(
                {
                  data: { "text/plain": reply },
                  metadata: {},
                  // @ts-ignore
                  execution_count: this.executionCount,
                },
                // @ts-ignore
                this.parentHeader
              );
              return {
                status: "ok",
                // @ts-ignore
                execution_count: this.executionCount,
                payload: [],
                user_expressions: {},
              };
            } catch (err: any) {
              const message = err?.message ?? String(err);
              // @ts-ignore
              this.publishExecuteError(
                {
                  ename: "Error",
                  evalue: message,
                  traceback: [],
                },
                // @ts-ignore
                this.parentHeader
              );
              return {
                status: "error",
                // @ts-ignore
                execution_count: this.executionCount,
                ename: "Error",
                evalue: message,
                traceback: [],
              };
            }
          }

          async kernelInfoRequest(): Promise<any> {
            return {
              status: "ok",
              protocol_version: "5.3",
              implementation: "webllm-lite-kernel",
              implementation_version: "0.1.0",
              language_info: {
                name: "markdown",
                version: "0.0.0",
                mimetype: "text/markdown",
                file_extension: ".md",
              },
              banner: "WebLLM-backed browser chat kernel",
              help_links: [],
            };
          }

          async completeRequest(content: any): Promise<any> {
            return {
              status: "ok",
              matches: [],
              cursor_start: content.cursor_pos ?? 0,
              cursor_end: content.cursor_pos ?? 0,
              metadata: {},
            };
          }

          async inspectRequest(_content: any): Promise<any> {
            return { status: "ok", found: false, data: {}, metadata: {} };
          }

          async isCompleteRequest(_content: any): Promise<any> {
            return { status: "complete", indent: "" };
          }

          async commInfoRequest(_content: any): Promise<any> {
            return { status: "ok", comms: {} };
          }

          async historyRequest(_content: any): Promise<any> {
            return { status: "ok", history: [] };
          }

          async shutdownRequest(_content: any): Promise<any> {
            return { status: "ok", restart: false };
          }

          async inputReply(_content: any): Promise<void> { }
          async commOpen(_content: any): Promise<void> { }
          async commMsg(_content: any): Promise<void> { }
          async commClose(_content: any): Promise<void> { }
        }

        // Define and return the plugin
        const httpChatKernelPlugin = {
          id: "http-chat-kernel:plugin",
          autoStart: true,
          // Match the official JupyterLite custom kernel pattern:
          // https://jupyterlite.readthedocs.io/en/latest/howto/extensions/kernel.html
          requires: [IKernelSpecs],
          activate: (app: any, kernelspecs: any) => {
            console.log("[http-chat-kernel] ===== ACTIVATE FUNCTION CALLED =====");
            console.log("[http-chat-kernel] JupyterLab app:", app);
            console.log("[http-chat-kernel] kernelspecs service:", kernelspecs);

            if (!kernelspecs || typeof kernelspecs.register !== "function") {
              console.error("[http-chat-kernel] ERROR: kernelspecs.register not available!");
              return;
            }

            try {
              kernelspecs.register({
                spec: {
                  name: "http-chat",
                  display_name: "HTTP Chat (ACP)",
                  language: "python",
                  argv: [],
                  resources: {},
                },
                create: async (options: any) => {
                  console.log("[http-chat-kernel] Creating HttpLiteKernel instance", options);
                  return new HttpLiteKernel(options);
                },
              });

              console.log("[http-chat-kernel] ===== KERNEL REGISTERED SUCCESSFULLY =====");
              console.log("[http-chat-kernel] Kernel name: http-chat");
              console.log("[http-chat-kernel] Display name: HTTP Chat (ACP)");
            } catch (error) {
              console.error("[http-chat-kernel] ===== REGISTRATION ERROR =====", error);
            }

            if (typeof document !== "undefined") {
              class WebLLMToolbarWidget extends ReactWidget {
                constructor() {
                  super();
                  // Make this widget look like the cell-type widget at the toolbar-item level
                  this.addClass("jp-Notebook-toolbarCellType");
                  this.addClass("webllm-model-toolbar");
                }
            
                render() {
                  const saved =
                    window.localStorage.getItem("webllm:modelId") ?? DEFAULT_WEBLLM_MODEL;
                
                  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
                    const value = event.target.value;
                    if (!value) {
                      return;
                    }
                    window.webllmModelId = value;
                    window.localStorage.setItem("webllm:modelId", value);
                  };
                
                  return React.createElement(
                    HTMLSelect,
                    {
                      className: "jp-Notebook-toolbarCellTypeDropdown",
                      defaultValue: saved,                // <- use defaultValue here
                      onChange: handleChange,
                      "aria-label": "WebLLM model",
                      title: "Select the WebLLM model",
                    },
                    WEBLLM_MODELS.map((id) =>
                      React.createElement("option", { key: id, value: id }, id)
                    )
                  );
                }
              }
            
              const webllmToolbarExtension = {
                createNew: (panel: any) => {
                  const widget = new WebLLMToolbarWidget();
            
                  // Position relative to other items; tweak index as desired
                  panel.toolbar.insertItem(10, "webllmModel", widget);
            
                  return widget;
                },
              };
            
              app.docRegistry.addWidgetExtension("Notebook", webllmToolbarExtension);
            
              // Progress text updates stay the same
              window.addEventListener("webllm:model-progress", (ev: any) => {
                const { progress: p, text } = ev.detail;
                const labels = document.querySelectorAll(
                  ".webllm-model-toolbar .jp-Notebook-toolbarCellTypeDropdown"
                ) as NodeListOf<HTMLSelectElement>;
            
                const suffix =
                  typeof p === "number" && p > 0 && p < 1
                    ? ` ${Math.round(p * 100)}%`
                    : p === 1
                    ? " ready"
                    : "";
            
                // Here I’m updating the <select> title, not the visible text (since options are the models).
                labels.forEach((el) => {
                  el.title = text ? `${text}${suffix}` : `WebLLM${suffix}`;
                });
              });
            }
            
      
      
          },
        };

        const plugins = [httpChatKernelPlugin];
        console.log("[lite-kernel/federation] ===== PLUGIN CREATED SUCCESSFULLY =====");
        console.log("[lite-kernel/federation] Plugin ID:", httpChatKernelPlugin.id);
        console.log("[lite-kernel/federation] Plugin autoStart:", httpChatKernelPlugin.autoStart);
        console.log("[lite-kernel/federation] Returning plugins array:", plugins);

        // IMPORTANT: Shape the exports like a real federated ES module
        // so JupyterLite's loader sees our plugins. It checks for
        // `__esModule` and then reads `.default`.
        const moduleExports = {
          __esModule: true,
          default: plugins
        };

        return moduleExports;
      };
    }

    throw new Error(`[lite-kernel/federation] Unknown module: ${module}`);
  }
};

// Register the container
window._JUPYTERLAB = window._JUPYTERLAB || {};
window._JUPYTERLAB[scope] = container;

console.log("[lite-kernel/federation] Registered Module Federation container for scope:", scope);
