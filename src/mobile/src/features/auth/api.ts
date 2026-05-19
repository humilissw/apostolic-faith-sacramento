import type { AxiosError } from 'axios';
import { createMutation } from 'react-query-kit';

import { client } from '@/lib/api';

export type LoginResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_token_expires: Date;
  refresh_token_expires: number;
  scopes: string[];
};

export type LoginVariables = {
  email: string;
  password: string;
};

export const useLogin = createMutation<LoginResponse, LoginVariables, AxiosError>({
  mutationFn: async ({ email, password }) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await client.post('/login/access-token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
});
