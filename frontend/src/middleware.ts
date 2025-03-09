import { defineMiddleware } from "astro/middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  if (
    context.request.method === "POST" &&
    context.request.headers.get("x-requested-with") === "django"
  ) {
    context.locals.django = await context.request.json();
  }

  return next();
});
