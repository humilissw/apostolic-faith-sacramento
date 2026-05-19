import type { AxiosError } from 'axios';
import { createQuery } from 'react-query-kit';

import { client } from '@/lib/api';

export type IntegrationConfig = {
  id: string;
  name: string;
  type: string;
  config: Record<string, unknown>;
  is_active: boolean;
  last_synced_at: string | null;
  created_on: string;
  updated_on: string | null;
};

export const useIntegrations = createQuery<IntegrationConfig[], void, AxiosError>({
  queryKey: ['integrations'],
  fetcher: () => client.get('/integrations').then(res => res.data.data),
});
