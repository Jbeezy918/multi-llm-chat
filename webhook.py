"""Stripe Webhook Handler - FastAPI Endpoint

This is a separate service that handles Stripe webhook events.
Deploy this independently on Railway, Fly.io, or Render.

Setup:
1. Deploy this file to your hosting platform
2. Set environment variables (STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, etc.)
3. Configure webhook URL in Stripe Dashboard: https://your-webhook-url.com/stripe/webhook
4. Select events to listen for:
   - checkout.session.completed
   - customer.subscription.updated
   - customer.subscription.deleted

Usage:
    uvicorn webhook:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.billing import (
    parse_webhook_event,
    handle_checkout_completed,
    handle_subscription_updated,
    handle_subscription_deleted
)
from core.subscriptions import SubscriptionManager

# Initialize FastAPI app
app = FastAPI(
    title="Multi-LLM Chat Stripe Webhooks",
    description="Webhook handler for Stripe billing events",
    version="1.0.0"
)

# Initialize subscription manager
subscription_manager = SubscriptionManager()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "stripe-webhook-handler",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "ok"}


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events

    This endpoint receives webhook events from Stripe and processes them.
    Events are verified using the webhook signing secret.

    Supported events:
    - checkout.session.completed: User completed payment
    - customer.subscription.updated: Subscription status changed
    - customer.subscription.deleted: Subscription canceled

    Returns:
        200 OK if event processed successfully
        400 Bad Request if payload is invalid
        500 Internal Server Error if processing fails
    """
    try:
        # Get raw body and signature
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")

        # Parse and verify webhook event
        event = parse_webhook_event(payload, sig_header)

        if not event:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        # Log event
        print(f"📨 Received Stripe webhook: {event['type']}")

        # Route event to appropriate handler
        event_type = event['type']

        if event_type == 'checkout.session.completed':
            success = handle_checkout_completed(event, subscription_manager)
            if success:
                print(f"✅ Checkout completed successfully")
                return JSONResponse(
                    status_code=200,
                    content={"status": "success", "event": "checkout_completed"}
                )
            else:
                print(f"❌ Failed to process checkout completion")
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "message": "Failed to process checkout"}
                )

        elif event_type == 'customer.subscription.updated':
            success = handle_subscription_updated(event, subscription_manager)
            if success:
                print(f"✅ Subscription updated successfully")
                return JSONResponse(
                    status_code=200,
                    content={"status": "success", "event": "subscription_updated"}
                )
            else:
                print(f"❌ Failed to process subscription update")
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "message": "Failed to process update"}
                )

        elif event_type == 'customer.subscription.deleted':
            success = handle_subscription_deleted(event, subscription_manager)
            if success:
                print(f"✅ Subscription deleted successfully")
                return JSONResponse(
                    status_code=200,
                    content={"status": "success", "event": "subscription_deleted"}
                )
            else:
                print(f"❌ Failed to process subscription deletion")
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "message": "Failed to process deletion"}
                )

        else:
            # Event type not handled - acknowledge receipt but don't process
            print(f"ℹ️ Unhandled event type: {event_type}")
            return JSONResponse(
                status_code=200,
                content={"status": "ignored", "event_type": event_type}
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"💥 Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
