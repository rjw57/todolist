// Custom node HTTP server for serving the server-side rendered UI.
//
// Django will launch this script passing a path to a Unix domain socket in the SOCKET_PATH
// environment variable. The server should bind a Unix domain socket to that path. Django assumes
// that the application is ready to serve once a HTTP request to "/" succeeds.
import { createServer } from "node:http";
import { handler } from "./dist/server/entry.mjs";

// Ensure we run and compiled JS in "production" mode.
process.env.NODE_ENV = "production";

const socket_path = process.env["SOCKET_PATH"];
if (!socket_path) {
  throw new Error("SOCKET_PATH environment variable must be defined");
}

createServer(handler).listen(socket_path);
