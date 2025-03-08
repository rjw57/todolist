import { defineMiddleware } from "astro/middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  // Do nothing if this result wasn't routed from a Django view.
  if (
    context.request.method !== "POST" ||
    context.request.headers.get("x-requested-with") !== "django"
  ) {
    return next();
  }

  context.locals.django = await context.request.json();

  return next();
});
