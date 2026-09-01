# EFT Payments - Stripe Integration

## Architecture

Donations are processed via Stripe through a client-server flow. The frontend (static Next.js export) communicates with the FastAPI backend, which handles all Stripe API calls and webhook verification.

## Stripe Setup

### Required Environment Variables

**Backend** (`.env`):
```
STRIPE_SECRET_KEY=sk_test_xxx          # Stripe API key
STRIPE_WEBHOOK_SECRET=whsec_xxx         # Webhook signing secret
STRIPE_CURRENCY=usd
```

**Frontend** (`.env`):
```
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_xxx  # Publishable key
```

### Stripe Resources to Create

1. **PaymentIntent** - One-time donations
2. **Checkout Session** - Recurring subscriptions
3. **Webhook endpoint** at `<backend-url>/api/v1/payments/webhook`

## Backend

### Models (`app/models.py`)

- **Payment** - Stores all payments (UUID PK, timestamps, Stripe IDs)
- **DonationConfig** - Preset donation amounts and labels

### API Routes (`app/api/routes/payments.py`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/payments/create-intent` | None | Create one-time payment |
| POST | `/payments/create-subscription` | None | Create recurring donation |
| POST | `/payments/webhook` | None | Stripe webhook handler |
| GET | `/payments/` | Required | User payment history |
| GET | `/payments/config` | None | Donation presets |

### Service Layer (`app/services/payment_service.py`)

- `create_payment_intent()` - Creates Stripe PaymentIntent
- `create_checkout_session()` - Creates Stripe Checkout Session
- `handle_webhook()` - Processes Stripe webhook events

### Repository (`app/repositories/payment_repo.py`)

`PaymentRepository` handles all database operations for payments.

## Frontend

### API Functions (`lib/api.ts`)

- `createPaymentIntent(data)` - POST to `/payments/create-intent`
- `createSubscription(data)` - POST to `/payments/create-subscription`
- `fetchDonationConfigs()` - GET `/payments/config`
- `fetchUserPayments()` - GET `/payments/` (with auth)

### Components

**DonationForm** (`components/donation-form.tsx`)
- Preset amounts: $10, $25, $50, $100, $250
- Frequency toggle: one-time / monthly
- Guest fields: name, email
- Stripe Elements card confirmation
- Loading, error, and success states

**DonationHistory** (`components/donation-history.tsx`)
- Displays user payment history
- Receipt links for succeeded payments

**DonationProvider** (`context/donation-context.tsx`)
- Global donation state management

### Donate Page (`app/(main)/donate/page.tsx`)
- Server component wrapper
- Shows DonationForm + DonationHistory (when authenticated)

## Payment Flow

### One-Time Donation
1. User enters amount and clicks "Donate"
2. Frontend calls `POST /payments/create-intent`
3. Backend creates Stripe PaymentIntent, returns `{ client_secret, payment_intent_id }`
4. Frontend loads Stripe, calls `stripe.confirmCardPayment(client_secret)`
5. Stripe processes payment, backend receives webhook
6. Frontend shows success message

### Recurring Donation
1. User selects "Monthly" frequency
2. Frontend calls `POST /payments/create-subscription`
3. Backend creates Stripe Checkout Session, returns checkout URL
4. Frontend redirects user to Stripe Checkout
5. Stripe processes subscription, backend receives webhook

## Webhook Events

- **`payment_intent.succeeded`** - Update Payment status to succeeded
- **`payment_intent.payment_failed`** - Update Payment status to failed
- **`invoice.payment_succeeded`** - Subscription payment succeeded
- **`invoice.payment_failed`** - Subscription payment failed

## Testing

```bash
# Backend tests
cd src/be && poetry run pytest

# Frontend tests
cd src/fe && bun test
```
