"""
Unit tests for SDK Wrapper module.
"""

from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest

from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK


@pytest.fixture
def sdk_wrapper():
    """Create a SafeClaudeSDK instance for testing."""
    return SafeClaudeSDK()


class TestSafeClaudeSDK:
    """Test SafeClaudeSDK class."""

    def test_init(self, sdk_wrapper):
        """Test SafeClaudeSDK initialization."""
        assert sdk_wrapper is not None

    @pytest.mark.asyncio
    async def test_run_basic(self, sdk_wrapper):
        """Test basic run operation."""
        prompt = "Test prompt"

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.return_value = MagicMock()

            result = await sdk_wrapper.run(prompt)

            assert result is not None
            mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_with_options(self, sdk_wrapper):
        """Test run with custom options."""
        prompt = "Test prompt"
        options = {"max_tokens": 1000}

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.return_value = MagicMock()

            result = await sdk_wrapper.run(prompt, options=options)

            assert result is not None

    @pytest.mark.asyncio
    async def test_run_handles_error(self, sdk_wrapper):
        """Test run handles errors gracefully."""
        prompt = "Test prompt"

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.side_effect = Exception("SDK Error")

            # Should handle error gracefully
            result = await sdk_wrapper.run(prompt)

            assert result is not None

    @pytest.mark.asyncio
    async def test_run_with_long_prompt(self, sdk_wrapper):
        """Test run with very long prompt."""
        long_prompt = "A" * 10000

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.return_value = MagicMock()

            result = await sdk_wrapper.run(long_prompt)

            assert result is not None

    @pytest.mark.asyncio
    async def test_run_multiple_times(self, sdk_wrapper):
        """Test running multiple times."""
        prompts = [f"Prompt {i}" for i in range(5)]

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.return_value = MagicMock()

            results = await asyncio.gather(*[
                sdk_wrapper.run(prompt) for prompt in prompts
            ])

            assert len(results) == 5
            assert mock_query.call_count == 5
