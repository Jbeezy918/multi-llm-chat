"""Stripe Billing Integration - Real Payment Rails"""
import os
import stripe
from typing import Optional, Dict, Any
from datetime import datetime


# Initialize Stripe with secret key from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Stripe price IDs from environment
STRIPE_PRICES = {
    "premium": os.getenv("STRIPE_PRICE_PREMIUM"),
    "team": os.getenv("STRIPE_PRICE_TEAM"),
    "pro": os.getenv("STRIPE_PRICE_PRO")
}

# Webhook secret for signature verification
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Success and cancel URLs
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", os.getenv("APP_URL", "http://localhost:8501") + "?billing=success")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", os.getenv("APP_URL", "http://localhost:8501") + "?billing=cancel")


def create_checkout_session(email: str, tier: str, subscription_manager) -> Optional[str]:
    """Create Stripe checkout session for subscription upgrade

    Args:
        email: User email address
        tier: Target subscription tier (premium, team, pro)
        subscription_manager: SubscriptionManager instance to update on success

    Returns:
        Checkout session URL or None if error
    """
    if not stripe.api_key:
        raise ValueError("STRIPE_SECRET_KEY not configured")

    if tier not in STRIPE_PRICES or not STRIPE_PRICES[tier]:
        raise ValueError(f"Stripe price not configured for tier: {tier}")

    try:
        # Get or create subscription record to attach metadata
        subscription = subscription_manager.get_subscription(email)
        if not subscription:
            subscription_manager.create_subscription(email, tier="free")

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{
                "price": STRIPE_PRICES[tier],
                "quantity": 1
            }],
            customer_email=email,
            success_url=STRIPE_SUCCESS_URL + f"&email={email}&tier={tier}",
            cancel_url=STRIPE_CANCEL_URL + f"&email={email}&tier={tier}",
            metadata={
                "user_email": email,
                "target_tier": tier,
                "source": "multi_llm_chat"
            },
            subscription_data={
                "metadata": {
                    "user_email": email,
                    "tier": tier
                }
            }
        )

        return checkout_session.url

    except stripe.error.StripeError as e:
        print(f"Stripe checkout session creation failed: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error creating checkout session: {str(e)}")
        return None


def parse_webhook_event(payload: bytes, sig_header: str) -> Optional[stripe.Event]:
    """Parse and verify Stripe webhook event

    Args:
        payload: Raw request body bytes
        sig_header: Stripe-Signature header value

    Returns:
        Verified Stripe event or None if verification fails
    """
    if not STRIPE_WEBHOOK_SECRET:
        raise ValueError("STRIPE_WEBHOOK_SECRET not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )
        return event

    except ValueError as e:
        print(f"Invalid webhook payload: {str(e)}")
        return None
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid webhook signature: {str(e)}")
        return None


def handle_checkout_completed(event: stripe.Event, subscription_manager) -> bool:
    """Handle successful checkout completion

    When customer completes payment:
    1. Extract customer email and tier from session metadata
    2. Get Stripe customer ID and subscription ID
    3. Upgrade local subscription to paid tier
    4. Store Stripe IDs for future reference

    Args:
        event: Stripe checkout.session.completed event
        subscription_manager: SubscriptionManager instance

    Returns:
        True if handled successfully, False otherwise
    """
    try:
        session = event['data']['object']

        # Extract metadata
        email = session.get('metadata', {}).get('user_email') or session.get('customer_email')
        tier = session.get('metadata', {}).get('target_tier')

        if not email or not tier:
            print(f"Missing email or tier in checkout session: {session['id']}")
            return False

        # Get Stripe IDs
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')

        # Upgrade subscription in local system
        success = subscription_manager.upgrade_subscription(email, tier)

        if success:
            # Store Stripe IDs in subscription record
            subscription_manager.update_stripe_data(
                email=email,
                customer_id=customer_id,
                subscription_id=subscription_id,
                payment_status="active"
            )

            print(f"✅ Checkout completed: {email} upgraded to {tier}")
            print(f"   Customer ID: {customer_id}")
            print(f"   Subscription ID: {subscription_id}")
            return True
        else:
            print(f"❌ Failed to upgrade subscription for {email}")
            return False

    except Exception as e:
        print(f"Error handling checkout completed: {str(e)}")
        return False


def handle_subscription_updated(event: stripe.Event, subscription_manager) -> bool:
    """Handle subscription update events

    Triggered when:
    - Subscription status changes (active, past_due, canceled, etc.)
    - Customer upgrades/downgrades plan
    - Payment fails/succeeds

    Args:
        event: Stripe customer.subscription.updated event
        subscription_manager: SubscriptionManager instance

    Returns:
        True if handled successfully, False otherwise
    """
    try:
        subscription = event['data']['object']

        # Extract metadata
        email = subscription.get('metadata', {}).get('user_email')
        tier = subscription.get('metadata', {}).get('tier')
        status = subscription.get('status')

        if not email:
            print(f"Missing email in subscription update: {subscription['id']}")
            return False

        # Update payment status
        subscription_manager.update_stripe_data(
            email=email,
            payment_status=status
        )

        # Handle status changes
        if status == 'active':
            if tier:
                # Ensure local tier matches Stripe
                local_sub = subscription_manager.get_subscription(email)
                if local_sub and local_sub.get('tier') != tier:
                    subscription_manager.upgrade_subscription(email, tier)
                    print(f"✅ Synced tier for {email}: {tier}")

        elif status in ['past_due', 'unpaid']:
            print(f"⚠️ Payment issue for {email}: {status}")
            # Could send email notification here

        elif status in ['canceled', 'incomplete_expired']:
            # Downgrade to free tier
            subscription_manager.downgrade_subscription(email, 'free')
            print(f"⬇️ Subscription canceled for {email}, downgraded to free")

        return True

    except Exception as e:
        print(f"Error handling subscription updated: {str(e)}")
        return False


def handle_subscription_deleted(event: stripe.Event, subscription_manager) -> bool:
    """Handle subscription deletion/cancellation

    When customer cancels:
    1. Downgrade to free tier
    2. Clear Stripe IDs
    3. Update payment status to canceled

    Args:
        event: Stripe customer.subscription.deleted event
        subscription_manager: SubscriptionManager instance

    Returns:
        True if handled successfully, False otherwise
    """
    try:
        subscription = event['data']['object']

        # Extract email from metadata
        email = subscription.get('metadata', {}).get('user_email')

        if not email:
            print(f"Missing email in subscription deletion: {subscription['id']}")
            return False

        # Downgrade to free tier
        subscription_manager.downgrade_subscription(email, 'free')

        # Update Stripe data
        subscription_manager.update_stripe_data(
            email=email,
            payment_status="canceled"
        )

        print(f"❌ Subscription deleted for {email}, downgraded to free")
        return True

    except Exception as e:
        print(f"Error handling subscription deleted: {str(e)}")
        return False


def create_customer_portal_session(email: str, subscription_manager) -> Optional[str]:
    """Create Stripe customer portal session for self-service management

    Allows customers to:
    - Update payment method
    - View invoice history
    - Cancel subscription

    Args:
        email: User email address
        subscription_manager: SubscriptionManager instance

    Returns:
        Customer portal URL or None if error
    """
    if not stripe.api_key:
        raise ValueError("STRIPE_SECRET_KEY not configured")

    try:
        subscription = subscription_manager.get_subscription(email)

        if not subscription or not subscription.get('stripe_customer_id'):
            print(f"No Stripe customer ID found for {email}")
            return None

        customer_id = subscription['stripe_customer_id']

        # Create portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=os.getenv("APP_URL", "http://localhost:8501")
        )

        return portal_session.url

    except stripe.error.StripeError as e:
        print(f"Failed to create customer portal session: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error creating portal session: {str(e)}")
        return None


def get_stripe_subscription_status(email: str, subscription_manager) -> Dict[str, Any]:
    """Get current Stripe subscription status for user

    Args:
        email: User email address
        subscription_manager: SubscriptionManager instance

    Returns:
        Dictionary with subscription status details
    """
    subscription = subscription_manager.get_subscription(email)

    if not subscription:
        return {
            "has_stripe_subscription": False,
            "status": "none",
            "tier": "free"
        }

    stripe_sub_id = subscription.get('stripe_subscription_id')

    if not stripe_sub_id:
        return {
            "has_stripe_subscription": False,
            "status": subscription.get('payment_status', 'none'),
            "tier": subscription.get('tier', 'free')
        }

    try:
        # Fetch live status from Stripe
        stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)

        return {
            "has_stripe_subscription": True,
            "status": stripe_sub.status,
            "tier": subscription.get('tier'),
            "current_period_end": stripe_sub.current_period_end,
            "cancel_at_period_end": stripe_sub.cancel_at_period_end
        }

    except stripe.error.StripeError as e:
        print(f"Failed to retrieve Stripe subscription: {str(e)}")
        return {
            "has_stripe_subscription": True,
            "status": "error",
            "tier": subscription.get('tier', 'free'),
            "error": str(e)
        }


def verify_stripe_config() -> Dict[str, bool]:
    """Verify Stripe configuration is complete

    Returns:
        Dictionary showing which config values are set
    """
    return {
        "stripe_secret_key": bool(stripe.api_key),
        "webhook_secret": bool(STRIPE_WEBHOOK_SECRET),
        "price_premium": bool(STRIPE_PRICES.get("premium")),
        "price_team": bool(STRIPE_PRICES.get("team")),
        "price_pro": bool(STRIPE_PRICES.get("pro")),
        "success_url": bool(STRIPE_SUCCESS_URL),
        "cancel_url": bool(STRIPE_CANCEL_URL)
    }


def is_stripe_configured() -> bool:
    """Check if Stripe is fully configured and ready to use

    Returns:
        True if all required Stripe config is present
    """
    config = verify_stripe_config()
    required = ["stripe_secret_key", "price_premium", "price_team", "price_pro"]
    return all(config.get(key, False) for key in required)
