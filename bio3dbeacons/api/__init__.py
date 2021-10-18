import asyncio
import json
import logging
import os
from ssl import AF_INET
from typing import Any, Optional

import aiohttp
from aiohttp.client import ClientTimeout
from aiohttp.client_exceptions import ClientResponseError

from bio3dbeacons.api.config.config import Config

print("ENV--> ", os.environ)
SOLR_COLLECTION_URL = os.environ.get("SOLR_COLLECTION_URL")
LOG_LEVEL = os.environ.get("LOG_LEVEL")
SOLR_USER = os.environ.get("SOLR_USER")
SOLR_PASS = os.environ.get("SOLR_PASS")


logger = logging.getLogger("3dbeacons-client")

if LOG_LEVEL:
    logger.setLevel(LOG_LEVEL)
else:
    logger.setLevel(logging.INFO)


class SolrError(Exception):
    """An exception occurred while talking to SOLR."""

    def __init__(self, reason, response):
        self.reason = reason
        self.response = response

    def __str__(self):
        return "{}: {}".format(self.reason, self.response)


class SingletonAiohttp:
    sem: Optional[asyncio.Semaphore] = asyncio.Semaphore(
        int(Config.get_config_val("main", "ASYNCIO_SEMAPHORE_COUNT"))
    )
    aiohttp_client: Optional[aiohttp.ClientSession] = None

    @classmethod
    def get_aiohttp_client(cls) -> aiohttp.ClientSession:
        if cls.aiohttp_client is None:
            timeout = ClientTimeout(
                total=float(Config.get_config_val("main", "DEFAULT_SOLR_TIMEOUT"))
            )
            connector = aiohttp.TCPConnector(
                family=AF_INET,
                verify_ssl=False,
            )
            cls.aiohttp_client = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                # auth=aiohttp.BasicAuth(SOLR_USER, SOLR_PASS),
            )

        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls) -> None:
        if cls.aiohttp_client:
            await cls.aiohttp_client.close()
            cls.aiohttp_client = None

    @classmethod
    async def query_url(cls, url: str) -> Any:
        client = cls.get_aiohttp_client()
        async with cls.sem:
            async with client.get(
                url,
                headers={
                    "content-type": "application/json",
                },
            ) as response:
                try:
                    response_payload = await response.text()
                    response.raise_for_status()
                    logger.debug(f"Received SOLR response for {url}")
                    return json.loads(response_payload)
                except ClientResponseError:
                    logger.debug(await response.text())
                    raise SolrError("SOLR returned an error", response)
                except json.decoder.JSONDecodeError:
                    raise SolrError("Cannot decode JSON from SOLR", response)
