"""
Test class for AsyncFetcher.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import pytest

from ahttpdc.read.fetch.fetcher import AsyncFetcher


class TestAsyncFetcher:
    """Test class for AsyncFetcher class from ahttpdc.read.fetch.fetcher
    module."""

    def set_up(self):
        """Set the AsyncFetcher object up for testing."""
        self.dev_url = 'http://localhost:9000/circumstances'
        self.fetcher = AsyncFetcher(
            self.dev_url,
        )

    @pytest.mark.asyncio
    async def test_request_null(self):
        """Test method for AsyncFetcher class and its only method."""
        self.set_up()
        request = await self.fetcher.request_readings()
        assert request is not None, 'request empty'

    @pytest.mark.asyncio
    async def test_request_json(self):
        """Test method to check if request is a dictionary."""
        self.set_up()
        request = await self.fetcher.request_readings()
        assert isinstance(request, dict)
