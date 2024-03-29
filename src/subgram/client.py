import asyncio
import logging
from typing import AsyncGenerator, Optional

import httpx

from subgram.schemas import CheckoutPageResponse, Event


class Subgram:

    BASE_URL = "https://api.subgram.io"

    def __init__(self, api_token):
        self.api_token = api_token

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.BASE_URL, timeout=10.0)

    async def has_access(
        self,
        user_id: int,
        product_id: int,
    ) -> bool:
        async with self.client as client:
            response = await client.get(
                f"/api/v1/{self.api_token}/products/{product_id}/{user_id}",
            )

            if response.status_code != 200:
                return False

            subscription_status = response.json()
            return subscription_status.get("has_access", False)

    async def create_checkout_page(
        self,
        product_id: int,
        user_id: int,  # telegram user id
        name: str,
        language_code: Optional[str] = None,
    ) -> CheckoutPageResponse:
        async with self.client as client:
            response = await client.post(
                f"/api/v1/{self.api_token}/products/{product_id}",
                json={
                    "user_id": user_id,
                    "name": name,
                    "language_code": language_code,
                },
            )
            return CheckoutPageResponse.model_validate_json(response.read())

    async def event_listener(self, timeout: float = 2) -> AsyncGenerator[Event, None]:
        event_id = 0
        async with self.client as client:
            while True:
                try:
                    response = await client.get(
                        f"/api/v1/{self.api_token}/events",
                        params={"event_id": event_id},
                    )
                    polling_response = response.json()
                except Exception as e:
                    logging.warning(f"Subgram API is not available, reason: {e}")
                    await asyncio.sleep(timeout * 10)
                    continue

                for event_data in polling_response.get("result", []):
                    event = Event.model_validate(event_data)
                    event_id = event.event_id
                    yield event

                await asyncio.sleep(timeout)
