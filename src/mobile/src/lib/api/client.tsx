import type { AxiosRequestConfig } from 'axios';
import type { TokenType } from '@/lib/auth/utils';
import axios from 'axios';
import Env from 'env';
import { signIn, signOut, useAuthStore } from '@/features/auth/use-auth-store';

export const client = axios.create({
  baseURL: Env.EXPO_PUBLIC_API_URL,
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (reason: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    }
    else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
}

client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token?.access) {
    config.headers.Authorization = `Bearer ${token.access}`;
  }
  return config;
});

client.interceptors.response.use(
  response => response,
  async (error) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return client(originalRequest);
          })
          .catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const storedToken = useAuthStore.getState().token;
      if (!storedToken?.refresh) {
        signOut();
        return Promise.reject(error);
      }

      try {
        const { data } = await client.post('/login/refresh-token', {
          refresh_token: storedToken.refresh,
        });

        const newToken: TokenType = {
          access: data.access_token,
          refresh: storedToken.refresh,
        };
        signIn(newToken);

        processQueue(null, data.access_token);

        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return client(originalRequest);
      }
      catch (err) {
        processQueue(err, null);
        signOut();
        return Promise.reject(err);
      }
      finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);
