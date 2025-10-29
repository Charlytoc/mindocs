import os
import stripe
from typing import Optional, Dict
from datetime import datetime, timedelta
from server.models import User, SubscriptionPlan
from server.utils.printer import Printer

printer = Printer("STRIPE_SERVICE")

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class StripeService:
    """Servicio para gestionar operaciones con Stripe"""

    @staticmethod
    def create_checkout_session(user_id: str, plan_id: str, plan_price_usd: float) -> str:
        """
        Crea una sesión de checkout de Stripe
        
        Args:
            user_id: ID del usuario
            plan_id: ID del plan
            plan_price_usd: Precio del plan en USD
            
        Returns:
            URL de checkout
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"MindDocs Subscription",
                            },
                            "unit_amount": int(plan_price_usd * 100),  # Convert to cents
                            "recurring": {
                                "interval": "month",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/subscription?success=true",
                cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/subscription?canceled=true",
                client_reference_id=user_id,
                metadata={
                    "user_id": user_id,
                    "plan_id": plan_id,
                },
            )
            
            printer.green(f"Created checkout session {session.id} for user {user_id}")
            return session.url
            
        except stripe.error.StripeError as e:
            printer.error(f"Stripe error creating checkout session: {e}")
            raise

    @staticmethod
    def create_customer_portal_session(stripe_customer_id: str) -> str:
        """
        Crea una sesión del portal de gestión de Stripe para el cliente
        
        Args:
            stripe_customer_id: ID del cliente en Stripe
            
        Returns:
            URL del portal
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=stripe_customer_id,
                return_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/subscription",
            )
            
            printer.green(f"Created portal session for customer {stripe_customer_id}")
            return session.url
            
        except stripe.error.StripeError as e:
            printer.error(f"Stripe error creating portal session: {e}")
            raise

    @staticmethod
    def handle_webhook(payload: bytes, signature: str) -> Dict:
        """
        Procesa un webhook de Stripe
        
        Args:
            payload: Body del webhook
            signature: Firma del webhook
            
        Returns:
            Evento procesado
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            printer.green(f"Webhook event: {event['type']}")
            return event
            
        except ValueError as e:
            printer.error(f"Invalid payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            printer.error(f"Invalid signature: {e}")
            raise

    @staticmethod
    def create_customer(email: str, name: Optional[str] = None) -> stripe.Customer:
        """
        Crea un cliente en Stripe
        
        Args:
            email: Email del cliente
            name: Nombre del cliente (opcional)
            
        Returns:
            Objeto Customer de Stripe
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
            )
            
            printer.green(f"Created Stripe customer {customer.id} for {email}")
            return customer
            
        except stripe.error.StripeError as e:
            printer.error(f"Stripe error creating customer: {e}")
            raise

    @staticmethod
    def get_subscription(stripe_subscription_id: str) -> stripe.Subscription:
        """
        Obtiene una suscripción de Stripe
        
        Args:
            stripe_subscription_id: ID de la suscripción
            
        Returns:
            Objeto Subscription de Stripe
        """
        try:
            subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            return subscription
            
        except stripe.error.StripeError as e:
            printer.error(f"Stripe error retrieving subscription: {e}")
            raise

    @staticmethod
    def cancel_subscription(stripe_subscription_id: str) -> stripe.Subscription:
        """
        Cancela una suscripción de Stripe
        
        Args:
            stripe_subscription_id: ID de la suscripción
            
        Returns:
            Suscripción cancelada
        """
        try:
            subscription = stripe.Subscription.modify(
                stripe_subscription_id,
                cancel_at_period_end=True,
            )
            
            printer.yellow(f"Subscription {stripe_subscription_id} set to cancel at period end")
            return subscription
            
        except stripe.error.StripeError as e:
            printer.error(f"Stripe error canceling subscription: {e}")
            raise
