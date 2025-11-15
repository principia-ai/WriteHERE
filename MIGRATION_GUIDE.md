# WriteHERE Migration Guide: Minimax M2 + Jina.ai Integration

This guide helps you migrate from the original WriteHERE setup to the new version with **Minimax M2** model support and **Jina.ai** search integration.

## Table of Contents

1. [Overview](#overview)
2. [What's New](#whats-new)
3. [Configuration Setup](#configuration-setup)
4. [Using Minimax M2 Models](#using-minimax-m2-models)
5. [Using Jina.ai Search](#using-jinai-search)
6. [Migration Steps](#migration-steps)
7. [Compatibility](#compatibility)
8. [Troubleshooting](#troubleshooting)

## Overview

The enhanced version of WriteHERE adds two major new capabilities:

1. **Minimax M2 Model Support**: Use Minimax's powerful M2 models for text generation and reasoning
2. **Jina.ai Search Integration**: Enhanced web search with cleaner content extraction

Both features are **fully backward compatible** - your existing configurations will continue to work.

## What's New

### Minimax M2 LLM Client

- **Location**: `recursive/llm/minimax.py`
- **Features**:
  - Full support for Minimax M2 chat models
  - Embedding API support
  - Automatic caching for efficiency
  - Retry logic with exponential backoff
  - OpenAI-compatible interface

- **Supported Models**:
  - `abab6.5s-chat` - Standard chat model
  - `abab6.5g-chat` - Advanced chat model
  - Other Minimax models as they become available

### Jina.ai Search Integration

- **Location**: `recursive/executor/actions/jina_search.py`
- **Features**:
  - Clean, structured web search results via Jina Search API
  - Content extraction without ads/clutter via Jina Reader API
  - Parallel search for multiple queries
  - Automatic result selection and summarization
  - Compatible with existing WriteHERE framework

- **Benefits over traditional search**:
  - No HTML parsing needed
  - Better handling of modern JavaScript-heavy pages
  - Cleaner content extraction
  - More reliable results

## Configuration Setup

### Step 1: Update API Key Configuration

Edit your `recursive/api_key.env` file (create it from `api_key.env.example` if it doesn't exist):

```bash
# Existing keys
OPENAI=your_openai_key
CLAUDE=your_claude_key
SERPAPI=your_serpapi_key
GEMINI=your_gemini_key
OPENROUTER=your_openrouter_key

# New: Minimax M2 API key
MINIMAX_API_KEY=your_minimax_api_key_here

# New: Jina.ai API key
JINA_API_KEY=your_jina_api_key_here

# New: Search provider selection
SEARCH_PROVIDER=serpapi  # Options: jina, serpapi, searxng
```

### Step 2: Obtain API Keys

#### Minimax API Key

1. Visit [Minimax Platform](https://api.minimax.chat/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `api_key.env` file

#### Jina.ai API Key

1. Visit [Jina.ai](https://jina.ai/)
2. Sign up for an account
3. Access the API section
4. Generate an API key for Search and Reader APIs
5. Copy the key to your `api_key.env` file

> **Note**: Some Jina.ai APIs may work without authentication, but having an API key provides higher rate limits and better reliability.

## Using Minimax M2 Models

### Basic Usage

Simply specify a Minimax model name when running the engine:

```bash
cd recursive
python engine.py \
  --filename ../test_data/meta_fiction.jsonl \
  --output-filename ./project/story/output.jsonl \
  --done-flag-file ./project/story/done.txt \
  --model abab6.5s-chat \
  --mode story
```

### Available Models

- **abab6.5s-chat**: Suitable for general tasks, faster inference
- **abab6.5g-chat**: More powerful model for complex tasks

### Model Selection Logic

The system automatically detects Minimax models based on naming:

- Any model name containing `abab`, `minimax`, or `m2` will use `MinimaxM2Client`
- All other models continue to use `OpenAIApiProxy`

### Example: Generating a Report with Minimax

```bash
python engine.py \
  --filename ../test_data/qa_test.jsonl \
  --output-filename ./project/qa/result.jsonl \
  --done-flag-file ./project/qa/done.txt \
  --model abab6.5g-chat \
  --mode report
```

## Using Jina.ai Search

### Enabling Jina Search

Set the search provider in your `api_key.env`:

```bash
SEARCH_PROVIDER=jina
JINA_API_KEY=your_jina_api_key
```

### How It Works

When `SEARCH_PROVIDER=jina` is set:

1. The system will use `JinaBrowser` instead of `BingBrowser`
2. Search queries go to Jina.ai Search API
3. Content extraction uses Jina.ai Reader API
4. Results are automatically filtered and summarized

### Comparison: SerpAPI vs Jina.ai

| Feature | SerpAPI | Jina.ai |
|---------|---------|---------|
| Search Quality | Bing-based | Web-wide |
| Content Extraction | HTML parsing | Clean text extraction |
| Modern Pages | May struggle | Better handling |
| Rate Limits | Based on plan | Based on plan |
| Cost | Per search | Per search |

### Switching Between Search Providers

You can switch search providers at any time by changing `SEARCH_PROVIDER`:

```bash
# Use Jina.ai
SEARCH_PROVIDER=jina

# Use SerpAPI (original)
SEARCH_PROVIDER=serpapi

# Use SearXNG (self-hosted)
SEARCH_PROVIDER=searxng
```

No code changes needed - the framework automatically loads the correct search module.

## Migration Steps

### For Existing Users

1. **Backup your current configuration**:
   ```bash
   cp recursive/api_key.env recursive/api_key.env.backup
   ```

2. **Update your environment file**:
   ```bash
   # Add new keys to your api_key.env
   echo "MINIMAX_API_KEY=your_key_here" >> recursive/api_key.env
   echo "JINA_API_KEY=your_key_here" >> recursive/api_key.env
   echo "SEARCH_PROVIDER=serpapi" >> recursive/api_key.env
   ```

3. **Test the new features** (optional):
   ```bash
   # Test Minimax M2
   cd recursive
   python engine.py --model abab6.5s-chat --mode story --filename ../test_data/meta_fiction.jsonl --output-filename ./test_output.jsonl --done-flag-file ./test_done.txt
   ```

4. **Gradually adopt** new features:
   - Start with your existing setup (no changes needed)
   - Try Minimax models on non-critical tasks
   - Switch to Jina search when ready

### For New Users

Simply follow the standard setup instructions in [README.md](README.md) and configure all API keys from the start.

## Compatibility

### Backward Compatibility

✅ **Fully backward compatible**:
- Existing model configurations continue to work
- SerpAPI and SearXNG search still supported
- No breaking changes to the API or CLI

### Forward Compatibility

✅ **Easy to adopt new features**:
- Add Minimax support: Just set `MINIMAX_API_KEY`
- Add Jina search: Just set `JINA_API_KEY` and `SEARCH_PROVIDER=jina`
- Mix and match: Use Minimax with SerpAPI, or GPT-4 with Jina search

## Troubleshooting

### Minimax M2 Issues

#### Problem: "MINIMAX_API_KEY not found"

**Solution**: Make sure you've added your API key to `recursive/api_key.env`:
```bash
MINIMAX_API_KEY=your_actual_key_here
```

#### Problem: API returns 401 Unauthorized

**Solution**:
- Verify your API key is correct
- Check if your Minimax account has sufficient credits
- Ensure the API key has the correct permissions

#### Problem: "No 'choices' in response"

**Solution**: The Minimax API response format may differ. Check the logs for the actual response format and report the issue if needed.

### Jina.ai Search Issues

#### Problem: "JINA_API_KEY not found in environment variables"

**Solution**: This is just a warning. Jina.ai may work without a key, but with rate limits. Add your key for better performance:
```bash
JINA_API_KEY=your_actual_key_here
```

#### Problem: No search results returned

**Solution**:
- Check your internet connection
- Verify the Jina.ai service is available
- Try switching to SerpAPI temporarily: `SEARCH_PROVIDER=serpapi`
- Check logs for specific error messages

#### Problem: Content extraction fails

**Solution**:
- Some websites may block automated access
- Check if the URL is valid and accessible
- The system will skip failed pages automatically

### General Issues

#### Problem: Module import errors

**Solution**:
```bash
# Reinstall the package
cd /path/to/writehere
pip install -v -e .
```

#### Problem: Cache-related errors

**Solution**:
```bash
# Clear the cache
rm -rf recursive/project/*/cache/
```

## Best Practices

### When to Use Minimax M2

- ✅ Chinese language tasks (Minimax models excel at Chinese)
- ✅ Cost-sensitive projects (competitive pricing)
- ✅ Tasks requiring reasoning and analysis
- ❓ Compare quality with GPT-4/Claude for your specific use case

### When to Use Jina.ai Search

- ✅ Need cleaner content without ads/popups
- ✅ Working with modern JavaScript-heavy websites
- ✅ Want simpler, more maintainable search integration
- ✅ Need reliable content extraction

### Optimization Tips

1. **Use caching**: The system automatically caches LLM calls and search results
2. **Monitor costs**: Check your API usage regularly
3. **Start small**: Test with small datasets before scaling up
4. **Mix models**: Use different models for different task types

## Support

If you encounter issues not covered in this guide:

1. Check the [main README](README.md)
2. Review the [Troubleshooting Guide](TROUBLESHOOTING.md) (if available)
3. Open an issue on [GitHub](https://github.com/Digidai/writehere/issues)
4. Include:
   - Error messages
   - Configuration (without API keys)
   - Steps to reproduce

## Changelog

### Version with Minimax M2 + Jina.ai Integration

**New Features**:
- Added Minimax M2 LLM client (`recursive/llm/minimax.py`)
- Added Jina.ai search integration (`recursive/executor/actions/jina_search.py`)
- Added LLM factory function for automatic client selection
- Updated configuration examples

**Improvements**:
- Better error handling for API calls
- Enhanced logging for debugging
- More flexible search provider configuration

**Backward Compatibility**:
- All existing features continue to work
- No breaking changes to CLI or API

---

**Last Updated**: 2025-11-15
**Author**: Claude Code Agent
**Version**: 1.0
