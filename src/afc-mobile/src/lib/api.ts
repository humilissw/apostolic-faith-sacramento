const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'https://localhost:8000/';
const API_V1 = 'api/v1';

// --- Donation ---

export interface DonationConfig {
  id: string;
  label: string;
  amount_cents: number;
  is_default: boolean;
  frequency: 'one_time' | 'recurring';
  created_on: string;
}

export interface PaymentIntentResult {
  client_secret: string;
  payment_intent_id: string;
}

export async function fetchDonationConfigs(): Promise<DonationConfig[]> {
  const res = await fetch(`${API_BASE}${API_V1}/payments/config`);
  if (!res.ok) throw new Error('Failed to fetch donation configs');
  const body = await res.json();
  return body.data;
}

export async function createPaymentIntent(data: {
  amount_cents: number;
  currency: string;
  frequency: 'one_time' | 'recurring';
  donor_email?: string;
  donor_name?: string;
}): Promise<PaymentIntentResult> {
  const res = await fetch(`${API_BASE}${API_V1}/payments/create-intent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || 'Failed to create payment intent');
  }
  return res.json();
}

// --- Sermons / Media ---

export interface SermonVideo {
  id: string;
  upload_location: string;
  upload_name: string;
  speaker_name: string | null;
  media_association_date: string;
  created_on: string;
  updated_on: string | null;
  description: string | null;
  reference_text: string | null;
  owner_id: string;
  download_url: string;
}

export interface VideosResponse {
  data: SermonVideo[];
  count: number;
}

export async function fetchVideos(): Promise<VideosResponse> {
  const res = await fetch(`${API_BASE}${API_V1}/video-uploads/`);
  if (!res.ok) throw new Error('Failed to fetch videos');
  return res.json();
}

// --- Doctrines ---

export interface DoctrineItem {
  id: string;
  title: string;
  content: string;
  order: number;
}

export async function fetchDoctrines(): Promise<DoctrineItem[]> {
  // If backend has a doctrines endpoint, use it.
  // Otherwise return hardcoded data matching the web page.
  return [
    {
      id: '1',
      title: 'The Divine Trinity',
      content: 'There are three persons in the Godhead: the Father, the Son, and the Holy Ghost, and these three are one God, the same in essence, eternal.',
      order: 1,
    },
    {
      id: '2',
      title: 'The Holy Bible',
      content: 'The Holy Bible was written by men divinely inspired and is God\'s revelation of Himself to man. It is a perfect, truthful and authoritative treasure of divine instruction.',
      order: 2,
    },
    {
      id: '3',
      title: 'Man\'s Salvation',
      content: 'Man is lost after Adam\'s fall. But man may be saved through the living Christ.',
      order: 3,
    },
  ];
}

// --- Contact ---

export interface ChurchContact {
  address: string;
  mapsUrl: string;
  embedUrl: string;
  phone: string;
  email: string;
}

export async function fetchContact(): Promise<ChurchContact> {
  return {
    address: '7842 Elmont Ave, Elverta, CA 95626',
    mapsUrl: 'https://www.google.com/maps/search/?api=1&query=7842%20Elmont%20Ave,%20Elverta,%20CA%2095626',
    embedUrl: 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3113.280133482945!2d-121.46131482355433!3d38.71137695765789!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x809b2888f7a1ddb5%3A0x860cfaa4c9c406da!2sTrinity%20Apostolic%20Faith%20Church!5e0!3m2!1sen!2sus!4v1769206276874!5m2!1sen!2sus',
    phone: '(530) 515-8440',
    email: 'info@afcsac.com',
  };
}
