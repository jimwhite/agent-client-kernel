// lite-kernel/src/federation.ts
// Module Federation container for JupyterLite

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
        const { KernelMessage } = await importShared('@jupyterlab/services');

        console.log("[lite-kernel/federation] Got BaseKernel from shared scope:", BaseKernel);

        // Define ChatHttpKernel inline
        class ChatHttpKernel {
          endpoint: string;

          constructor(opts: any = {}) {
            this.endpoint = opts.endpoint ?? "http://localhost:8000/chat";
            console.log("[ChatHttpKernel] Using endpoint:", this.endpoint);
          }

          async send(prompt: string): Promise<string> {
            console.log("[ChatHttpKernel] Sending prompt:", prompt);
            const resp = await fetch(this.endpoint, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ prompt })
            });

            if (!resp.ok) {
              const text = await resp.text().catch(() => "");
              console.error("[ChatHttpKernel] HTTP error", resp.status, text);
              throw new Error(`HTTP ${resp.status}: ${text || resp.statusText}`);
            }

            const data = await resp.json();
            if (data.error) {
              console.error("[ChatHttpKernel] LLM error:", data.error, data.detail);
              throw new Error(`LLM error: ${data.error} – ${data.detail ?? ""}`);
            }

            const reply = data.reply ?? "";
            console.log("[ChatHttpKernel] Got reply:", reply);
            return reply;
          }
        }

        // Define HttpLiteKernel extending BaseKernel
        class HttpLiteKernel extends BaseKernel {
          private chat: ChatHttpKernel;

          constructor(options: any) {
            super(options);
            const endpoint = options.endpoint ?? "http://localhost:8000/chat";
            this.chat = new ChatHttpKernel({ endpoint });
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
              implementation: "http-lite-kernel",
              implementation_version: "0.1.0",
              language_info: {
                name: "markdown",
                version: "0.0.0",
                mimetype: "text/markdown",
                file_extension: ".md",
              },
              banner: "HTTP-backed LLM chat kernel",
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
