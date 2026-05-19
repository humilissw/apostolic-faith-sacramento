import type { AxiosError } from 'axios';
import { createMutation, createQuery } from 'react-query-kit';

import { client } from '@/lib/api';

export type Payment = {
  id: string;
  amount_cents: number;
  currency: string;
  status: string;
  stripe_payment_intent_id: string;
  donor_email: string;
  donor_name: string | null;
  created_on: string;
  updated_on: string | null;
};

export type PaymentIntentRequest = {
  amount_cents: number;
  currency: string;
  donor_email?: string;
  donor_name?: string;
};

export const usePaymentHistory = createQuery<Payment[], { skip?: number; limit?: number }, AxiosError>({
  queryKey: ['payment-history'],
  fetcher: variables =>
    client
      .get('/payments', { params: variables })
      .then(res => res.data),
});

export const useCreatePaymentIntent = createMutation<PaymentIntentRequest, PaymentIntentRequest, AxiosError>({
  mutationFn: async (variables) => {
    const response = await client.post('/payments/create-intent', variables);
    return response.data;
  },
});
