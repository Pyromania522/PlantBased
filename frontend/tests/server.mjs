import http from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
const root = process.cwd();
const server = http.createServer(async (req, res) => {
  const pathname = decodeURIComponent(
    new URL(req.url, "http://localhost").pathname,
  );
  const file = pathname.startsWith("/plantbased/")
    ? path.join(
        root,
        "custom_components/plantbased/frontend",
        pathname.slice("/plantbased/".length),
      )
    : pathname === "/"
      ? path.join(root, "frontend/tests/harness.html")
      : "";
  if (!file || !file.startsWith(root + path.sep) || pathname.includes("..")) {
    res.writeHead(404).end();
    return;
  }
  try {
    const body = await readFile(file);
    res.writeHead(200, {
      "Content-Type": file.endsWith(".js")
        ? "text/javascript"
        : file.endsWith(".svg")
          ? "image/svg+xml"
          : "text/html",
    });
    res.end(body);
  } catch {
    res.writeHead(404).end();
  }
});
server.listen(4173, "127.0.0.1");
