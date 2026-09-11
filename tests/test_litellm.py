"""Tests for the LiteLLM integration in OpenAIApiProxy."""

import sys
import types
from unittest import mock

import pytest


# Stub recursive.memory so llm.py can be imported without the full package
_mem = types.ModuleType("recursive")
sys.modules.setdefault("recursive", _mem)
_mem_memory = types.ModuleType("recursive.memory")


class _FakeCache:
    def __init__(self):
        self.store = {}

    def get_cache(self, name, args_dict):
        key = str(args_dict)
        return self.store.get(key)

    def save_cache(self, name, args_dict, value):
        key = str(args_dict)
        self.store[key] = value


_mem_memory.caches = {"llm": _FakeCache()}
sys.modules.setdefault("recursive.memory", _mem_memory)


def _make_response(content="Hello", prompt_tokens=10, completion_tokens=5):
    """Build a fake litellm.completion() response matching ModelResponse shape."""
    from types import SimpleNamespace

    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        ),
    )


def _load_proxy():
    """Import OpenAIApiProxy in isolation."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "llm", "recursive/llm/llm.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.OpenAIApiProxy


class TestLiteLLMRouting:
    """Verify the litellm/ prefix routes to _call_litellm."""

    def test_litellm_prefix_routes_correctly(self):
        Proxy = _load_proxy()
        proxy = Proxy(verbose=False)
        fake_resp = _make_response("test output")

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(return_value=fake_resp)

            result = proxy.call(
                model="litellm/anthropic/claude-sonnet-4-6",
                messages=[{"role": "user", "content": "hi"}],
                no_cache=True,
            )

        assert result == [{"message": {"content": "test output"}}]
        litellm.completion.assert_called_once()
        call_kwargs = litellm.completion.call_args
        assert call_kwargs[1]["model"] == "anthropic/claude-sonnet-4-6"

    def test_non_litellm_model_does_not_route_to_litellm(self):
        Proxy = _load_proxy()
        proxy = Proxy(verbose=False)
        proxy.MAX_RETRIES = 1

        with mock.patch.object(proxy, "_call_litellm") as mock_litellm, \
             mock.patch.object(proxy.session, "post", side_effect=Exception("blocked")):
            try:
                proxy.call(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": "hi"}],
                    no_cache=True,
                )
            except Exception:
                pass
            mock_litellm.assert_not_called()


class TestLiteLLMCallParams:
    """Verify correct params are passed to litellm.completion."""

    def test_drop_params_true_by_default(self):
        Proxy = _load_proxy()
        proxy = Proxy(verbose=False)
        fake_resp = _make_response()

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(return_value=fake_resp)

            proxy.call(
                model="litellm/openai/gpt-4o",
                messages=[{"role": "user", "content": "hi"}],
                no_cache=True,
            )

        call_kwargs = litellm.completion.call_args[1]
        assert call_kwargs["drop_params"] is True

    def test_temperature_forwarded(self):
        Proxy = _load_proxy()
        proxy = Proxy(verbose=False)
        fake_resp = _make_response()

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(return_value=fake_resp)

            proxy.call(
                model="litellm/openai/gpt-4o",
                messages=[{"role": "user", "content": "hi"}],
                no_cache=True,
                temperature=0.3,
            )

        call_kwargs = litellm.completion.call_args[1]
        assert call_kwargs["temperature"] == 0.3

    def test_temperature_omitted_when_none(self):
        Proxy = _load_proxy()
        proxy = Proxy(verbose=False)
        fake_resp = _make_response()

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(return_value=fake_resp)

            proxy.call(
                model="litellm/openai/gpt-4o",
                messages=[{"role": "user", "content": "hi"}],
                no_cache=True,
            )

        call_kwargs = litellm.completion.call_args[1]
        assert "temperature" not in call_kwargs

    def test_max_tokens_set_to_8192(self):
        Proxy = _load_proxy()
        proxy = Proxy(verbose=False)
        fake_resp = _make_response()

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(return_value=fake_resp)

            proxy.call(
                model="litellm/openai/gpt-4o",
                messages=[{"role": "user", "content": "hi"}],
                no_cache=True,
            )

        call_kwargs = litellm.completion.call_args[1]
        assert call_kwargs["max_tokens"] == 8192


class TestLiteLLMCaching:
    """Verify caching works for litellm calls."""

    def test_cache_hit_skips_api_call(self):
        Proxy = _load_proxy()
        proxy = Proxy(verbose=False)
        fake_resp = _make_response("first call")

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(return_value=fake_resp)

            result1 = proxy.call(
                model="litellm/openai/gpt-4o",
                messages=[{"role": "user", "content": "cached?"}],
                no_cache=False,
            )
            result2 = proxy.call(
                model="litellm/openai/gpt-4o",
                messages=[{"role": "user", "content": "cached?"}],
                no_cache=False,
            )

        assert result1 == result2
        assert litellm.completion.call_count == 1


class TestLiteLLMRetry:
    """Verify transient errors trigger retries, non-transient errors raise."""

    def test_non_transient_error_raises_immediately(self):
        Proxy = _load_proxy()
        proxy = Proxy(verbose=False)

        auth_error = type("AuthenticationError", (Exception,), {
            "__module__": "litellm.exceptions"
        })()

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(side_effect=auth_error)

            with pytest.raises(Exception):
                proxy.call(
                    model="litellm/openai/gpt-4o",
                    messages=[{"role": "user", "content": "hi"}],
                    no_cache=True,
                )

        assert litellm.completion.call_count == 1

    def test_transient_error_retries(self):
        Proxy = _load_proxy()
        proxy = Proxy(verbose=False)
        proxy.MAX_RETRIES = 3
        proxy.BACKOFF_FACTOR = 0

        rate_error = type("RateLimitError", (Exception,), {
            "__module__": "litellm.exceptions"
        })()
        fake_resp = _make_response("recovered")

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(
                side_effect=[rate_error, rate_error, fake_resp]
            )

            result = proxy.call(
                model="litellm/openai/gpt-4o",
                messages=[{"role": "user", "content": "hi"}],
                no_cache=True,
            )

        assert result == [{"message": {"content": "recovered"}}]
        assert litellm.completion.call_count == 3
