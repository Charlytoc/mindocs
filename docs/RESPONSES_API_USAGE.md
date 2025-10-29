# Responses API Usage Guide

## Overview

The Responses API implementation provides a V2 processor that uses OpenAI's new Responses API for workflow execution. This document explains how to enable and use this feature.

## Features

- **Class-based Architecture**: Clean, maintainable code structure
- **Responses API Integration**: Uses OpenAI's latest API for better performance
- **Backward Compatible**: V1 processor remains unchanged and functional
- **Easy Toggle**: Simple environment variable to switch between versions

## Enabling V2 Processor

To enable the V2 processor using the Responses API, set the following environment variable:

```bash
USE_RESPONSES_API=true
```

When this is set to `true`, all new workflow executions will use the V2 processor. When `false` (default), they will use the V1 processor.

## Environment Variables

```bash
# Enable V2 processor (false by default)
USE_RESPONSES_API=false

# Model configuration for V2
MODEL=gpt-4o-mini

# Maximum iterations for agent loop (V2 only)
RESPONSES_API_MAX_ITERATIONS=20

# API key for OpenAI
PROVIDER_API_KEY=sk-...
```

## How It Works

### V1 Processor (Current)
- Function-based architecture
- Uses Chat Completions API
- Located in `server/utils/processor.py`

### V2 Processor (New)
- Class-based architecture
- Uses Responses API
- Located in `server/utils/processor_v2.py`
- Mirrors all V1 functionality

## Differences from V1

While the functionality is identical, there are some architectural differences:

1. **Code Organization**: V2 uses classes instead of functions
2. **Agent Implementation**: New agent class (`WorkflowAgent`) handles the execution loop
3. **Service Layer**: Separate `ResponsesAPIService` handles API interactions
4. **Message Format**: Uses Responses API message format

## Testing

To test the V2 processor:

1. Set `USE_RESPONSES_API=true` in your environment
2. Start the application
3. Execute a workflow
4. Check logs for "V2" indicators

## Troubleshooting

### Processor Not Switching

**Symptom**: Workflows still using V1 even with `USE_RESPONSES_API=true`

**Solution**: 
- Restart the application after setting the environment variable
- Check logs for which processor is being used
- Verify the environment variable is set correctly

### API Errors

**Symptom**: API-related errors in V2

**Solution**:
- Ensure `PROVIDER_API_KEY` is set correctly
- Check API key has necessary permissions
- Verify model name in `MODEL` is valid

### Different Results

**Symptom**: V2 produces different outputs than V1

**Expected**: Results should be functionally identical, but may vary slightly due to:
- Different API endpoints
- Model behavior differences
- Message formatting differences

## Rollback

To rollback to V1:

1. Set `USE_RESPONSES_API=false`
2. Restart the application

All V1 code remains unchanged and functional.

## Future Enhancements

Planned features for V2:

- Image generation support
- Enhanced vision capabilities
- Streaming responses
- Better error handling
- Performance optimizations

## Support

For issues or questions about the V2 processor:

1. Check this documentation
2. Review logs for error messages
3. Compare with V1 behavior
4. Report issues with relevant logs
