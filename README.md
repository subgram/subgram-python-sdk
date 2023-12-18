# Subgram python sdk

This SDK will help you to integrate subscriptions into your Telegram bot.


## Init the module.

Get your `SUBGRAM_TOKEN`: https://t.me/subgram_merchant_bot

``` python
from subgram import Subgram

subgram = Subgram(SUBGRAM_TOKEN)
```


## Check if a user has paid

Get your `PRODUCT_ID`: https://t.me/subgram_merchant_bot

``` python
async def show_paid_functionallity(update, context):
    if await subgram.has_access(
        user_id=update.effective_user.id,
        product_id=SUBGRAM_PRODUCT_ID,
    ):
        await update.effective_user.send_message("You paid!")
```


## Create a checkout page

If you want to send to your user a checkout page link or if your user wants to manage a subscription (same link):


``` python
async def manage_subscription(update, context):
    checkout_page = await subgram.create_checkout_page(
        product_id=SUBGRAM_PRODUCT_ID,
        user_id=update.effective_user.id,
        name=update.effective_user.name,  # for invoices
        language_code=update.effective_user.language_code,  # for localization
    )

    await update.effective_user.send_message(
        "You can manage your subscription by clicking this button:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Manage Subscription", 
            web_app=WebAppInfo(url=checkout_page.checkout_url))
        ]]),
    )
```

## Listen to payment events

Instead of forcing your developers to rent a server, purchase a domain name and setting up SSL certificates for classic webhook updates, we replicated a long polling approach which is widely used among Telegram bot developers.


``` python
# define a function which will listen 
# to Subgram updates in the background
async def post_init(application: Application) -> None:
    asyncio.create_task(handle_subgram_events())

# best place to run it -- while building the Application:
def main() -> None:
    application = (
        Application
        .builder()
        .post_init(post_init)
        .token(settings.TELEGRAM_TOKEN)
        .build()
    )
    ...
```

In `handle_subgram_events` you should write your own handlers for each received event type. The function can look like this:

``` python
async def handle_subgram_events():
    bot = Bot(TELEGRAM_TOKEN)  # bot instance to send messages

    # Async Generator 
    async for event in subgram.event_listener():
        if event.type == EventType.SUBSCRIPTION_STARTED:
            await bot.send_message(
                chat_id=event.object.customer.telegram_id,
                text=f"Thank you for subscribing! You have access until: {event.object.status.ending_at}.",
            )
```

All event types are defined in src/subgram/constants.py:

``` python
# from subgram.constants import EventType

class EventType(str, Enum):
    SUBSCRIPTION_STARTED = "subscription.started"
    SUBSCRIPTION_RENEWED = "subscription.renewed"
    SUBSCRIPTION_RENEW_FAILED = "subscription.renew_failed"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    SUBSCRIPTION_UPGRADED = "subscription.upgraded"

```