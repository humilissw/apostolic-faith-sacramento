import { act } from 'react';
import { screen, setup, waitFor } from '@/lib/test-utils';
import { useLogin } from './api';
import { LoginScreen } from './login-screen';

// Mock the hooks
jest.mock('./api', () => ({
  useLogin: jest.fn(),
}));

jest.mock('./use-auth-store', () => ({
  useAuthStore: {
    use: {
      signIn: jest.fn(),
    },
    getState: jest.fn(() => ({
      signIn: jest.fn(),
      status: 'signOut',
      token: null,
    })),
  },
}));

/* eslint-disable react/no-unnecessary-use-prefix */
jest.mock('expo-router', () => ({
  useRouter: () => ({ replace: jest.fn() }),
  useFocusEffect: jest.fn(),
  useLinkBuilder: jest.fn(),
  useNavigationContext: jest.fn(),
}));
/* eslint-enable react/no-unnecessary-use-prefix */

const loginMock = useLogin as jest.MockedFunction<typeof useLogin>;

afterEach(() => {
  jest.clearAllMocks();
});

describe('loginScreen', () => {
  it('renders login form with title', async () => {
    loginMock.mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
      isError: false,
    });

    setup(<LoginScreen />);
    expect(await screen.findByTestId('form-title')).toBeOnTheScreen();
  });

  it('renders login button', async () => {
    loginMock.mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
      isError: false,
    });

    setup(<LoginScreen />);
    expect(screen.getByTestId('login-button')).toBeOnTheScreen();
  });

  it('renders email input', async () => {
    loginMock.mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
      isError: false,
    });

    setup(<LoginScreen />);
    expect(screen.getByTestId('email-input')).toBeOnTheScreen();
  });

  it('renders password input', async () => {
    loginMock.mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
      isError: false,
    });

    setup(<LoginScreen />);
    expect(screen.getByTestId('password-input')).toBeOnTheScreen();
  });

  it('shows loading text while logging in', async () => {
    loginMock.mockReturnValue({
      mutate: jest.fn(),
      isPending: true,
      isError: false,
    });

    setup(<LoginScreen />);
    expect(screen.getByText(/Signing in/i)).toBeOnTheScreen();
  });

  it('calls login mutation on submit', async () => {
    const mockMutate = jest.fn();
    loginMock.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
      isError: false,
    });

    const { user } = setup(<LoginScreen />);

    const button = screen.getByTestId('login-button');
    const emailInput = screen.getByTestId('email-input');
    const passwordInput = screen.getByTestId('password-input');

    // Simulate typing by triggering onChangeText handlers directly
    act(() => {
      emailInput.props?.onChangeText?.('test@example.com');
    });
    act(() => {
      passwordInput.props?.onChangeText?.('password123');
    });

    await user.press(button);

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalled();
    });
    expect(mockMutate).toHaveBeenCalledWith(
      { email: 'test@example.com', password: 'password123' },
      expect.any(Object),
    );
  });
});
