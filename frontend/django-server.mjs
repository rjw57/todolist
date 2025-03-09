// Custom node HTTP server for serving the server-side rendered UI.
//
// Django will launch this script passing a path to a Unix domain socket in the SOCKET_PATH
// environment variable. The server should bind a Unix domain socket to that path. Django assumes
// that the application is ready to serve once a HTTP request to "/" succeeds.
import express from "express";
import { handler } from "./dist/server/entry.mjs";

// Ensure we run in "production" mode.
process.env.NODE_ENV = "production";

// Extract the path to the Unix domain socket we need to listen on from the environment.
const socket_path = process.env["SOCKET_PATH"];
if (!socket_path) {
  throw new Error("SOCKET_PATH environment variable must be defined");
}

express().use(handler).listen(socket_path);
