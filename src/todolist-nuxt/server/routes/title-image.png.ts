import { readFile } from "node:fs/promises";

// Personalization (stage 8.0) mounts a ConfigMap with the title image here.
const TITLE_IMAGE = "/opt/images/title-image.png";

// GET /title-image.png: the mounted image, or the TodoList icon without one.
export default defineEventHandler(async (event) => {
  try {
    const image = await readFile(TITLE_IMAGE);
    setResponseHeader(event, "Content-Type", "image/png");
    return image;
  } catch {
    return sendRedirect(event, "/favicon.ico");
  }
});
