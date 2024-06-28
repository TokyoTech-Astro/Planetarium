import { z } from 'zod';
import { procedure, router } from './trpc';
const { exec } = require('node:child_process')

export const appRouter = router({
  hello: procedure
    .input(
      z.object({
        text: z.string(),
      }),
    )
    .query((opts) => {
      return {
        greeting: `hello ${opts.input.text}`
      };
    }),
});

// export type definition of API
export type AppRouter = typeof appRouter;