/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_DWANI_API_BASE_URL: string;
    readonly VITE_DWANI_API_KEY: string;
    readonly VITE_UBERTAX_BACKEND_APP_API_URL: string;
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }