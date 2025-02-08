import React from "react";
import { createRoot } from "react-dom/client";
import * as DjangoBridge from "@django-bridge/react";

import "./index.css";
import App from "./App";
import * as serviceWorker from "./serviceWorker";

const config = new DjangoBridge.Config();

// Add your views here
config.addView("Home", App);

const rootElement = document.getElementById("root")!;
const initialResponse = JSON.parse(
  document.getElementById("initial-response")!.textContent!
);

createRoot(rootElement).render(
  <React.StrictMode>
    <DjangoBridge.App config={config} initialResponse={initialResponse} />
  </React.StrictMode>
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
