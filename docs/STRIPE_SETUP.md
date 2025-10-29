# Stripe Integration Guide

This guide will walk you through setting up Stripe for subscription management in MindDocs.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Stripe Account Setup](#stripe-account-setup)
3. [Getting API Keys](#getting-api-keys)
4. [Configuring Webhooks](#configuring-webhooks)
5. [Environment Variables](#environment-variables)
6. [Testing with Stripe Test Cards](#testing-with-stripe-test-cards)
7. [Production Deployment](#production-deployment)

## Prerequisites

- A Stripe account (sign up at [stripe.com](https://stripe.com))
- Your MindDocs application running locally
- Access to your `.env` file

## Stripe Account Setup

1. Sign up for a Stripe account at https://stripe.com
2. Complete your business information in the Stripe Dashboard
3. Verify your email address

## Getting API Keys

1. Log in to your Stripe Dashboard
2. Click on "Developers" in the left sidebar
3. Click on "API keys"
4. You'll see two keys:
   - **Publishable key** (starts with `pk_test_` or `pk_live_`)
   - **Secret key** (starts with `sk_test_` or `sk_live_`)

**Important**: For development, use the **Test** keys (they contain `_test_`).

Copy the Secret key to your `.env` file as `STRIPE_SECRET_KEY`.

## Configuring Webhooks

Webhooks allow Stripe to notify your application about subscription events (payment succeeded, subscription cancelled, etc.).

### For Local Development

1. Install the Stripe CLI from https://stripe.com/docs/stripe-cli
2. Run the following command to log in:
   ```bash
   stripe login
   ```
3. Forward Stripe events to your local server:
   ```bash
   stripe listen --forward-to localhost:8000/api/webhooks/stripe
   ```
4. Copy the webhook signing secret (starts with `whsec_`) displayed in the terminal
5. Add it to your `.env` file as `STRIPE_WEBHOOK_SECRET`

### For Production

1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Enter your webhook URL: `https://yourdomain.com/api/webhooks/stripe`
4. Select the following events to listen to:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **Add endpoint**
6. Copy the **Signing secret** (starts with `whsec_`)
7. Add it to your production environment variables as `STRIPE_WEBHOOK_SECRET`

## Environment Variables

Add these variables to your `.env` file:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Frontend URL (for redirects after payment)
FRONTEND_URL=http://localhost:5173
```

## Testing with Stripe Test Cards

Stripe provides test card numbers you can use without making real charges:

### Successful Payment

Use any of these card numbers:
- `4242 4242 4242 4242` - Visa
- `5555 5555 5555 4444` - Mastercard
- `3782 822463 10005` - American Express

For any test card:
- Use any **future expiration date** (e.g., 12/25)
- Use any **3 or 4 digit CVC**
- Use any **ZIP code**

### Declined Payment

- Use card number: `4000 0000 0000 9995`
- This will result in a declined payment

### Authentication Required (3D Secure)

- Use card number: `4000 0025 0000 3155`
- This will require authentication

### Complete List

See all test cards at: https://stripe.com/docs/testing

## Production Deployment

When you're ready to accept real payments:

1. Switch to **Live mode** in your Stripe Dashboard
2. Get your **Live** API keys (they start with `pk_live_` and `sk_live_`)
3. Update your environment variables:
   ```env
   STRIPE_SECRET_KEY=sk_live_your_live_secret_key_here
   ```
4. Update your webhook endpoint in Stripe Dashboard to use your production URL
5. Get the production webhook signing secret and update it
6. Test the webhook is working correctly

## Troubleshooting

### Webhook Not Receiving Events

1. Check that the webhook URL is correct in Stripe Dashboard
2. Verify the webhook signing secret is correct
3. Check your server logs for errors
4. Make sure your server is accessible from the internet (for production)

### Payment Succeeds but Credits Not Added

1. Check the webhook logs in Stripe Dashboard
2. Verify the webhook handler is processing events correctly
3. Check your database for any errors
4. Review your server logs

### Test Cards Not Working

1. Make sure you're using the exact card numbers listed above
2. Ensure you're in **Test mode** in Stripe Dashboard
3. Check that your Stripe API key starts with `sk_test_`

## Security Best Practices

1. **Never commit your secret keys** to version control
2. Use **environment variables** for all sensitive data
3. **Always verify webhook signatures** (already implemented in our code)
4. Use **HTTPS** in production
5. Regularly **rotate your API keys** if they're compromised

## Additional Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe CLI Documentation](https://stripe.com/docs/stripe-cli)

## Support

If you encounter issues:
1. Check the [Stripe Status Page](https://status.stripe.com/)
2. Review the error messages in your logs
3. Consult the [Stripe Documentation](https://stripe.com/docs)
4. Contact Stripe Support through your Dashboard
