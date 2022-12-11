/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly BASE_URL: string;
  readonly APP_TITLE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
