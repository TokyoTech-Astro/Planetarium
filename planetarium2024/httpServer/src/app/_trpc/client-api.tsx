import { createTRPCReact } from "@trpc/react-query";

import { type AppRouter } from "@/server/api";

export const clientApi = createTRPCReact<AppRouter>({});