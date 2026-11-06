declare module "legacy-lib" {
  export function load(id: string): Promise<string>;
}
