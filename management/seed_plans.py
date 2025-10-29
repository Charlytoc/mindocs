import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.db import get_session
from server.models import SubscriptionPlan, SubscriptionPlanType


async def seed_plans():
    """Seed initial subscription plans"""
    async for session in get_session():
        try:
            # Check if plans already exist
            from sqlalchemy import select
            
            result = await session.execute(select(SubscriptionPlan))
            existing = result.scalars().all()
            
            if existing:
                print("Plans already exist. Skipping seed.")
                return
            
            # Define plans
            plans = [
                {
                    "plan_type": SubscriptionPlanType.FREE,
                    "name": "Free Plan",
                    "description": "Get started with 1,000 credits to explore MindDocs",
                    "price_usd": 0.00,
                    "monthly_credits": 1000,  # $10 worth
                    "estimated_cost_usd": 0.00,
                    "margin_percentage": 0.00,
                    "features": {
                        "max_workflows": 3,
                        "max_executions_per_month": 10,
                        "ai_models": ["gpt-3.5-turbo"],
                        "support": "community"
                    }
                },
                {
                    "plan_type": SubscriptionPlanType.BASIC,
                    "name": "Basic Plan",
                    "description": "Perfect for individuals and small teams",
                    "price_usd": 29.99,
                    "monthly_credits": 5000,  # $50 worth
                    "estimated_cost_usd": 21.00,
                    "margin_percentage": 30.00,
                    "features": {
                        "max_workflows": 10,
                        "max_executions_per_month": 50,
                        "ai_models": ["gpt-3.5-turbo", "gpt-4"],
                        "support": "email"
                    }
                },
                {
                    "plan_type": SubscriptionPlanType.PRO,
                    "name": "Pro Plan",
                    "description": "Advanced features for power users",
                    "price_usd": 99.99,
                    "monthly_credits": 25000,  # $250 worth
                    "estimated_cost_usd": 70.00,
                    "margin_percentage": 30.00,
                    "features": {
                        "max_workflows": 50,
                        "max_executions_per_month": 250,
                        "ai_models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                        "support": "priority",
                        "custom_ai_models": True
                    }
                },
                {
                    "plan_type": SubscriptionPlanType.ENTERPRISE,
                    "name": "Enterprise Plan",
                    "description": "Custom solutions for large organizations",
                    "price_usd": 299.99,
                    "monthly_credits": 100000,  # $1,000 worth
                    "estimated_cost_usd": 210.00,
                    "margin_percentage": 30.00,
                    "features": {
                        "max_workflows": -1,  # Unlimited
                        "max_executions_per_month": -1,  # Unlimited
                        "ai_models": ["all"],
                        "support": "dedicated",
                        "custom_ai_models": True,
                        "sso": True,
                        "custom_integrations": True,
                        "dedicated_support": True
                    }
                },
            ]
            
            # Create plan objects
            for plan_data in plans:
                plan = SubscriptionPlan(**plan_data)
                session.add(plan)
            
            await session.commit()
            
            print("Successfully seeded subscription plans:")
            for plan_data in plans:
                print(f"  - {plan_data['name']}: ${plan_data['price_usd']}/month ({plan_data['monthly_credits']} credits)")
            
        except Exception as e:
            await session.rollback()
            print(f"Error seeding plans: {e}")
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(seed_plans())
