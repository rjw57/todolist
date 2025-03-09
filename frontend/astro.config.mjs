// @ts-check
import { defineConfig } from "astro/config";
import react from "@astrojs/react";

import node from "@astrojs/node";

// https://astro.build/config
export default defineConfig({
  // Enable React to support React JSX components.
  integrations: [react()],

  // Since we always pass a Django context to the rendered pages, set the default to server-side
  // rendering for all pages. If you escape from the Django harness, you may want to change this.
  // See: https://docs.astro.build/en/guides/on-demand-rendering/.
  output: "server",

  vite: {
    server: {
      hmr: {
        // This is only required if we're using Django. Essentially we can't proxy WebSocket
        // connections via Django and so this option ensures that the WebSocket connection used for
        // HMR goes to the "real" dev server exposed on localhost:4321 rather than the proxied one
        // on localhost:8000.
        clientPort: 4321,
      },
    },
  },

  devToolbar: {
    // The dev toolbar doesn't bring us anything at the moment since we aren't heavy users of
    // server-side islands.
    enabled: false,
  },

  adapter: node({
    mode: "middleware",
  }),
});
