let sharedScope: any = null;

const MINIMUM_VERSIONS: Record<string, string> = {
  "@jupyterlab/coreutils": "6.4.9",
  "@jupyterlab/application": "4.4.9",
  "@jupyterlab/ui-components": "4.4.9",
  "@jupyterlab/services": "7.4.9",
  "@jupyterlab/settingregistry": "4.4.9",
  "@jupyterlab/notebook": "4.4.9",
  "@jupyterlab/apputils": "4.5.9",
};

export function setSharedScope(scope: any) {
  sharedScope = scope;
  normalizeSharedScopeVersions();
}

function ensureScope(): any {
  if (!sharedScope) {
    throw new Error("[lite-kernel] Shared scope has not been initialised");
  }
  return sharedScope;
}

export function getSharedModule<T = any>(moduleName: string): T {
  const scope = ensureScope();
  const versions = scope[moduleName];
  if (!versions) {
    throw new Error(`[lite-kernel] Module ${moduleName} not found in shared scope`);
  }
  const versionKeys = Object.keys(versions);
  if (versionKeys.length === 0) {
    throw new Error(`[lite-kernel] No versions available for ${moduleName}`);
  }
  const selected = versions[versionKeys[0]];
  const factory = selected?.get;
  if (typeof factory !== "function") {
    throw new Error(`[lite-kernel] Shared module ${moduleName} missing factory`);
  }
  const moduleExports = factory();
  if (moduleExports && typeof (moduleExports as Promise<any>).then === "function") {
    throw new Error("[lite-kernel] Async shared modules are not supported");
  }
  return moduleExports as T;
}

function normalizeSharedScopeVersions() {
  const scope = sharedScope;
  if (!scope) {
    return;
  }
  for (const [moduleName, targetVersion] of Object.entries(MINIMUM_VERSIONS)) {
    coerceModuleVersion(scope, moduleName, targetVersion);
  }
}

function coerceModuleVersion(scope: any, moduleName: string, targetVersion: string) {
  const versions = scope[moduleName];
  if (!versions) {
    return;
  }
  if (versions[targetVersion]) {
    return;
  }
  const available = Object.keys(versions);
  if (available.length === 0) {
    return;
  }
  available.sort(compareVersions);
  const best = available[available.length - 1];
  versions[targetVersion] = versions[best];
}

function compareVersions(a: string, b: string): number {
  const aParts = a.split(".").map((part) => parseInt(part, 10) || 0);
  const bParts = b.split(".").map((part) => parseInt(part, 10) || 0);
  const len = Math.max(aParts.length, bParts.length);
  for (let i = 0; i < len; i++) {
    const diff = (aParts[i] ?? 0) - (bParts[i] ?? 0);
    if (diff !== 0) {
      return diff;
    }
  }
  return 0;
}
