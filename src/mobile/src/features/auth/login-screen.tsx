import type { LoginFormProps } from './components/login-form';

import { useRouter } from 'expo-router';

import * as React from 'react';
import { showMessage } from 'react-native-flash-message';

import { FocusAwareStatusBar, Text, View } from '@/components/ui';
import { showErrorMessage } from '@/components/ui/utils';
import { useLogin } from './api';
import { LoginForm } from './components/login-form';
import { useAuthStore } from './use-auth-store';

export function LoginScreen() {
  const router = useRouter();
  const signIn = useAuthStore.use.signIn();
  const { mutate: login, isPending } = useLogin();

  const onSubmit: LoginFormProps['onSubmit'] = (data) => {
    login(
      { email: data.email, password: data.password },
      {
        onSuccess: (data) => {
          signIn({ access: data.access_token, refresh: data.refresh_token });
          showMessage({
            message: 'Login successful',
            type: 'success',
          });
          router.replace('/profile');
        },
        onError: () => {
          showErrorMessage('Invalid email or password');
        },
      },
    );
  };

  return (
    <>
      <FocusAwareStatusBar />
      <View className="flex-1 justify-center">
        <LoginForm onSubmit={onSubmit} />
        {isPending && (
          <Text className="mt-4 text-center text-neutral-500">
            Signing in...
          </Text>
        )}
      </View>
    </>
  );
}
