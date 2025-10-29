# Credits and Subscription System

## Overview

MindDocs implements a credit-based subscription system where users purchase plans that provide monthly credits. Credits are used to pay for AI-powered workflows and services.

## Credit Model

- **1 Credit = $0.01 USD**
- Credits are consumed based on actual usage (OpenAI tokens, image processing, etc.)
- Users can subscribe to monthly plans that automatically add credits each month
- No consumption limits - users can spend all their credits immediately if desired

## Database Models

### SubscriptionPlan
Defines available subscription plans:
- `plan_type`: FREE, BASIC, PRO, ENTERPRISE
- `price_usd`: Monthly subscription price
- `monthly_credits`: Number of credits added each month
- `estimated_cost_usd`: Internal cost estimate
- `margin_percentage`: Profit margin target

### UserSubscription
Tracks active user subscriptions:
- Links user to a subscription plan
- Stores Stripe subscription ID
- Tracks subscription status (ACTIVE, CANCELLED, etc.)
- Records billing period dates

### CreditBalance
Stores each user's current credit balance:
- `balance`: Current number of credits
- Automatically created when needed
- Tracks last credit/debit timestamps

### CreditTransaction
Complete audit trail of all credit transactions:
- Adds (positive) and subtracts (negative) credits
- Tracks transaction type, description, metadata
- Records balance before/after each transaction
- Links to related workflow executions or subscriptions

## Services

### CreditService

Located in `server/services/credit_service.py`:

```python
# Get user's current balance
balance = await CreditService.get_user_balance(session, user_id)

# Add credits to user
await CreditService.add_credits(
    session,
    user_id,
    credits=1000,
    transaction_type=CreditTransactionType.SUBSCRIPTION_RENEWAL,
    description="Monthly subscription credits",
    subscription_id=subscription_id
)

# Consume credits
try:
    await CreditService.consume_credits(
        session,
        user_id,
        credits=100,
        transaction_type=CreditTransactionType.WORKFLOW_EXECUTION,
        execution_id=execution_id,
        description="Workflow execution cost"
    )
except HTTPException as e:
    # Insufficient credits
    pass
```

### StripeService

Located in `server/services/stripe_service.py`:

Handles all Stripe operations:
- Creating checkout sessions
- Processing webhooks
- Managing customer portal access
- Canceling subscriptions

## API Endpoints

### Credits

- `GET /api/user/credits` - Get current balance
- `GET /api/user/credit-history` - Transaction history

### Subscriptions

- `GET /api/subscription-plans` - List all plans (public)
- `GET /api/user/subscription` - Get user's subscription
- `POST /api/subscription/create-checkout` - Create Stripe checkout
- `POST /api/subscription/cancel` - Cancel subscription
- `POST /api/subscription/manage` - Get customer portal link
- `POST /api/webhooks/stripe` - Stripe webhook handler

## Workflow Integration

**Note**: Credit consumption in workflow execution is NOT yet implemented. This is planned for a future phase.

When implemented, workflows will consume credits based on:
- Number of AI API calls made
- Tokens processed
- Image processing operations
- Audio transcription length

## Subscription Plans

### Free Plan - $0/month
- 1,000 credits ($10 value)
- 3 workflows max
- 10 executions/month
- GPT-3.5-turbo only

### Basic Plan - $29.99/month
- 5,000 credits ($50 value)
- 10 workflows max
- 50 executions/month
- GPT-3.5 and GPT-4

### Pro Plan - $99.99/month
- 25,000 credits ($250 value)
- 50 workflows max
- 250 executions/month
- All AI models
- Priority support

### Enterprise Plan - $299.99/month
- 100,000 credits ($1,000 value)
- Unlimited workflows
- Unlimited executions
- All features
- Dedicated support
- SSO and custom integrations

## Setup Instructions

1. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "add_subscription_and_credit_models"
   alembic upgrade head
   ```

2. **Seed plans**:
   ```bash
   python management/seed_plans.py
   ```

3. **Configure Stripe** (see `docs/STRIPE_SETUP.md`)

4. **Environment variables**:
   ```env
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   FRONTEND_URL=http://localhost:5173
   ```

## Docker Development

Use the provided taskfile for development:

```bash
# Start development environment
./taskfile dev

# Run migrations
./taskfile migrate

# Seed plans
./taskfile seed

# View logs
./taskfile logs

# See all commands
./taskfile help
```

## Frontend Integration

The frontend needs to:
1. Display credit balance in the navbar
2. Show subscription management page
3. Implement Stripe checkout flow
4. Display transaction history

API functions are in `client/src/utils/api.ts` (to be implemented).

## Testing

### Local Testing
1. Use Stripe test mode keys
2. Use Stripe CLI to forward webhooks locally
3. Test with Stripe test cards (4242 4242 4242 4242)

### Stripe Test Cards
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 9995`
- 3D Secure: `4000 0025 0000 3155`

See full list at https://stripe.com/docs/testing

## Future Enhancements

- [ ] Integrate credit consumption in workflow execution
- [ ] Add credit packages for one-time purchases
- [ ] Implement usage-based pricing calculator
- [ ] Add credit refunds for failed operations
- [ ] Create admin panel for credit adjustments
- [ ] Add credit expiration policies
- [ ] Implement referral credit bonuses

## Security Considerations

1. All credit operations are audited in `CreditTransaction`
2. Stripe webhooks verify signatures
3. Credit balances are validated before consumption
4. No double-spending possible with database transactions
5. All credit operations use user's session authentication

## Monitoring

Monitor these key metrics:
- Total credits issued per period
- Average credits consumed per user
- Subscription churn rate
- Cost per credit vs revenue per credit
- Credit balance distribution
