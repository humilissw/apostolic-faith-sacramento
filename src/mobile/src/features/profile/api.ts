import type { AxiosError } from 'axios';
import { createQuery } from 'react-query-kit';

import { client } from '@/lib/api';

export type UserProfileData = {
  email: string;
  is_active: boolean;
  id: string;
  new_id: string;
  full_name: string | null;
  assigned_scopes: string[];
};

export const useUserProfile = createQuery<UserProfileData, void, AxiosError>({
  queryKey: ['user-profile'],
  fetcher: () => client.get('/auth/me').then(res => res.data),
});
