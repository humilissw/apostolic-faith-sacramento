import type { AxiosError } from 'axios';
import { createMutation, createQuery } from 'react-query-kit';

import { client } from '@/lib/api';

export type Assignment = {
  id: string;
  user_id: string;
  event_date: string;
  type: string;
  role: string;
  instrument: string | null;
  notes: string | null;
  group_leader: boolean;
  created_on: string;
  updated_on: string | null;
};

export type TimeOffRequest = {
  id: string;
  user_id: string;
  date: string;
  status: string;
  notes: string | null;
  created_on: string;
  updated_on: string | null;
};

export const useMyCalendar = createQuery<Assignment[], { startDate: string; endDate: string }, AxiosError>({
  queryKey: ['my-calendar'],
  fetcher: variables =>
    client
      .get('/scheduler/my-calendar', { params: variables })
      .then(res => res.data.data),
});

export const useMyAssignments = createQuery<Assignment[], void, AxiosError>({
  queryKey: ['my-assignments'],
  fetcher: () => client.get('/scheduler/my-assignments').then(res => res.data.data),
});

export const useMyTimeOff = createQuery<TimeOffRequest[], void, AxiosError>({
  queryKey: ['my-time-off'],
  fetcher: () => client.get('/scheduler/time-off-requests').then(res => res.data.data),
});

export const useCreateTimeOff = createMutation<TimeOffRequest, { date: string; notes?: string }, AxiosError>({
  mutationFn: async (variables) => {
    const response = await client.post('/scheduler/time-off-request', {
      date: variables.date,
      notes: variables.notes,
    });
    return response.data;
  },
});
