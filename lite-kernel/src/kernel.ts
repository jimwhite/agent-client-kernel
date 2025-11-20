// lite-kernel/src/kernel.ts
import { BaseKernel, IKernel } from "@jupyterlite/kernel";
import { ChatHttpKernel } from "./ChatHttpKernel.js";

type KernelOptions = IKernel.IOptions & {
  /**
   * Optional WebLLM model identifier to pass through to ChatHttpKernel.
   */
  model?: string;
};

export class HttpLiteKernel extends BaseKernel {
  private chat: ChatHttpKernel;

  constructor(options: KernelOptions) {
    super(options);
    const model = options.model;
    this.chat = new ChatHttpKernel({ model });
  }

  async executeRequest(content: any): Promise<any> {
    const code = String(content.code ?? "");
    try {
      const reply = await this.chat.send(code);
      this.publishExecuteResult(
        {
          data: { "text/plain": reply },
          metadata: {},
          execution_count: this.executionCount,
        },
        this.parentHeader
      );
      return {
        status: "ok",
        execution_count: this.executionCount,
        payload: [],
        user_expressions: {},
      };
    } catch (err: any) {
      const message = err?.message ?? String(err);
      this.publishExecuteError(
        {
          ename: "Error",
          evalue: message,
          traceback: [],
        },
        this.parentHeader
      );
      return {
        status: "error",
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
    return {
      status: "ok",
      found: false,
      data: {},
      metadata: {},
    };
  }

  async isCompleteRequest(_content: any): Promise<any> {
    return {
      status: "complete",
      indent: "",
    };
  }

  async commInfoRequest(_content: any): Promise<any> {
    return {
      status: "ok",
      comms: {},
    };
  }

  async historyRequest(_content: any): Promise<any> {
    return {
      status: "ok",
      history: [],
    };
  }

  async shutdownRequest(_content: any): Promise<any> {
    return {
      status: "ok",
      restart: false,
    };
  }

  async inputReply(_content: any): Promise<void> {}

  async commOpen(_content: any): Promise<void> {}
  async commMsg(_content: any): Promise<void> {}
  async commClose(_content: any): Promise<void> {}
}

export function createHttpLiteKernel(options: KernelOptions): IKernel {
  return new HttpLiteKernel(options);
}
