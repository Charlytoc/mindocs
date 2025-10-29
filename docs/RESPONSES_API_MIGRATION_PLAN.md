# Migration Plan: OpenAI Responses API Integration

## Overview

This document outlines the migration plan to integrate OpenAI's new Responses API for image generation and vision capabilities into the MindDocs platform.

## Current State

- Using traditional OpenAI Completions/Chat API
- No image generation capabilities
- Limited multimodal support
- Processing PDFs, images, and audio separately with different utilities

## Target State

- Migrate to OpenAI Responses API
- Integrate GPT Image 1 for image generation
- Support vision capabilities across all workflows
- Allow agents to automatically decide when to use image generation
- Maintain backward compatibility with existing workflows

## Key Benefits

1. **Native Multimodal Support**: Better handling of images, text, and audio
2. **Image Generation**: Built-in capability to generate and edit images
3. **Multi-turn Editing**: Iterative image refinement through conversation
4. **Automatic Tool Selection**: AI decides when to generate images
5. **World Knowledge**: Better understanding for realistic image generation

## Migration Phases

### Phase 1: Infrastructure Setup (Days 1-2)

#### 1.1 Update OpenAI Service

**File**: `server/utils/openai_service.py` or create `server/services/openai_responses_service.py`

**Tasks**:
- [ ] Install/update `openai` package to latest version (>=1.79.0)
- [ ] Create new service for Responses API
- [ ] Implement `create_response()` method
- [ ] Support streaming responses
- [ ] Handle image generation tool outputs
- [ ] Support vision (image input) capabilities

**Key Methods**:
```python
def create_response(
    input_data: List[Message],
    tools: Optional[List[Dict]],
    model: str,
    instructions: str,
    store: bool = False,
    previous_response_id: Optional[str] = None,
    stream: bool = False,
) -> ResponseObject

def process_image_generation(output: ResponseOutputItem) -> Dict
```

#### 1.2 Update Agent Base Class

**File**: `server/utils/agent.py` (or similar)

**Tasks**:
- [ ] Update agent to support Responses API
- [ ] Add automatic image generation tool
- [ ] Handle image generation outputs
- [ ] Support multi-turn image editing
- [ ] Integrate vision capabilities

**Key Changes**:
```python
# Add image generation tool
IMAGE_GENERATION_TOOL = {
    "type": "image_generation",
    "quality": "auto",
    "size": "auto",
    "background": "auto"
}

# Agent automatically decides when to use it
tools = [IMAGE_GENERATION_TOOL] + custom_tools
```

### Phase 2: Image Generation Integration (Days 3-4)

#### 2.1 Add Image Generation Utility

**File**: `server/utils/image_generator.py` (new)

**Features**:
- [ ] Generate images from text prompts
- [ ] Edit existing images
- [ ] Support multi-turn editing
- [ ] Handle image outputs (save to storage)
- [ ] Support different quality/size options

**Key Methods**:
```python
async def generate_image(
    prompt: str,
    quality: str = "auto",
    size: str = "auto",
    previous_image_id: Optional[str] = None
) -> Dict

async def edit_image(
    prompt: str,
    image_path: str,
    mask_path: Optional[str] = None,
    input_fidelity: str = "low"
) -> Dict
```

#### 2.2 Update Workflow Processor

**File**: `server/utils/processor.py`

**Changes**:
- [ ] Detect when AI wants to generate images
- [ ] Process image generation tool calls
- [ ] Save generated images as assets
- [ ] Link images to workflow executions

### Phase 3: Vision Capabilities (Days 5-6)

#### 3.1 Update Image Reader

**File**: `server/utils/image_reader.py`

**Enhancements**:
- [ ] Use Responses API for vision
- [ ] Support multiple images per request
- [ ] Configure detail level (low/high/auto)
- [ ] Better OCR and text extraction
- [ ] Object detection and scene understanding

#### 3.2 Update PDF Reader

**File**: `server/utils/pdf_reader.py`

**Changes**:
- [ ] Use vision for PDF pages
- [ ] Extract images from PDFs
- [ ] Analyze complex layouts
- [ ] Better table extraction

### Phase 4: Workflow Enhancements (Days 7-8)

#### 4.1 New Workflow Types

**Create workflows that leverage images**:
- [ ] Design generation workflows
- [ ] Image editing workflows
- [ ] Visual content analysis
- [ ] Document design automation

**Example**: "Generate a professional presentation design based on this document"

#### 4.2 Update Existing Workflows

**Enhance current workflows**:
- [ ] Add image generation to text workflows
- [ ] Support visual outputs for reports
- [ ] Generate diagrams and charts
- [ ] Create visual summaries

### Phase 5: Frontend Updates (Days 9-10)

#### 5.1 Asset Display

**File**: `client/src/components/AssetDisplay.tsx`

**Updates**:
- [ ] Display generated images
- [ ] Support image preview
- [ ] Download generated images
- [ ] Show generation metadata

#### 5.2 Workflow UI

**File**: `client/src/components/WorkflowBuilder/WorkflowBuilder.tsx`

**Changes**:
- [ ] Add image generation instructions
- [ ] Configure quality/size options
- [ ] Preview generated images
- [ ] Support multi-turn editing

### Phase 6: Testing & Optimization (Days 11-12)

#### 6.1 Testing

- [ ] Test image generation with various prompts
- [ ] Test image editing workflows
- [ ] Test vision capabilities
- [ ] Test multi-turn conversations
- [ ] Load testing for concurrent requests

#### 6.2 Cost Optimization

- [ ] Monitor image generation costs
- [ ] Implement caching for repeated requests
- [ ] Optimize detail levels
- [ ] Add usage tracking

#### 6.3 Error Handling

- [ ] Handle API rate limits
- [ ] Manage content moderation
- [ ] Graceful degradation
- [ ] User-friendly error messages

## Code Examples

### Basic Image Generation

```python
from server.services.openai_responses_service import ResponsesService

async def generate_image_for_workflow(execution_id: str, prompt: str):
    service = ResponsesService()
    
    response = await service.create_response(
        input_data=[{
            "role": "user",
            "content": [{"type": "input_text", "text": prompt}]
        }],
        tools=[{"type": "image_generation", "quality": "high"}],
        model="gpt-5",
        instructions="You are a helpful assistant that generates images."
    )
    
    # Process output
    for output in response.output:
        if output.type == "image_generation_call":
            image_data = output.result
            # Save image
            image_path = save_image(image_data, execution_id)
            return image_path
```

### Multi-turn Image Editing

```python
# First generation
response1 = await service.create_response(
    input_data=[{
        "role": "user",
        "content": [{"type": "input_text", "text": "Create a logo for a tech startup"}]
    }],
    tools=[{"type": "image_generation"}],
    model="gpt-5"
)

# Refine based on previous response
response2 = await service.create_response(
    previous_response_id=response1.id,
    input_data=[{
        "role": "user",
        "content": [{"type": "input_text", "text": "Make it more modern and blue"}]
    }],
    tools=[{"type": "image_generation"}],
    model="gpt-5"
)
```

### Vision Analysis

```python
# Analyze uploaded image
response = await service.create_response(
    input_data=[{
        "role": "user",
        "content": [
            {"type": "input_text", "text": "What's in this image? Provide a detailed analysis."},
            {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{base64_image}",
                "detail": "high"
            }
        ]
    }],
    model="gpt-4.1-mini",
    instructions="You are an expert at analyzing images."
)
```

## Configuration

### Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# Image Generation
OPENAI_IMAGE_QUALITY=auto
OPENAI_IMAGE_SIZE=auto
OPENAI_IMAGE_BACKGROUND=auto
OPENAI_IMAGE_MAX_TOKENS=6240  # For high quality

# Vision
OPENAI_VISION_DETAIL=auto
OPENAI_VISION_MAX_SIZE_MB=50
```

### Model Selection

```python
IMAGE_GENERATION_MODEL = "gpt-5"  # For image generation
VISION_MODEL = "gpt-4.1-mini"      # For vision tasks
TEXT_GENERATION_MODEL = "gpt-4.1-mini"  # For text tasks
```

## Cost Considerations

### Image Generation Costs (GPT Image)

| Quality | Square (1024×1024) | Portrait (1024×1536) | Landscape (1536×1024) |
|---------|-------------------|---------------------|----------------------|
| Low     | 272 tokens        | 408 tokens          | 400 tokens           |
| Medium  | 1056 tokens       | 1584 tokens         | 1568 tokens          |
| High    | 4160 tokens       | 6240 tokens         | 6208 tokens          |

### Vision Costs

- **Low detail**: 85 tokens (fixed)
- **High detail**: 85 + (tiles × 170) tokens
- Based on image size and detail level

### Recommendations

1. Use "auto" quality by default
2. Use "low" detail for simple queries
3. Cache generated images
4. Monitor usage per user
5. Implement rate limiting

## Rollout Strategy

### Phase 1: Internal Testing (Week 1)
- Migrate in development environment
- Test with internal users
- Monitor costs and performance

### Phase 2: Beta Users (Week 2)
- Enable for beta testers
- Collect feedback
- Fix issues

### Phase 3: Gradual Rollout (Week 3)
- Enable for 25% of users
- Monitor metrics
- Increase to 100%

### Phase 4: Full Release (Week 4)
- All users have access
- Documentation updated
- Training materials available

## Rollback Plan

If issues arise:

1. **Immediate**: Disable image generation feature flag
2. **Short-term**: Revert to previous OpenAI API version
3. **Medium-term**: Fix issues and redeploy
4. **Long-term**: Improve error handling and monitoring

## Success Metrics

- [ ] 90% of image generation requests succeed
- [ ] Average generation time < 30 seconds
- [ ] User satisfaction score > 4/5
- [ ] Cost per image < $0.10
- [ ] Zero critical bugs in production

## Documentation Updates

- [ ] Update API documentation
- [ ] Create image generation guide
- [ ] Update workflow templates
- [ ] Add examples and tutorials
- [ ] Update developer docs

## Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Infrastructure | 2 days | Responses API service |
| 2. Image Generation | 2 days | Image generation features |
| 3. Vision | 2 days | Vision capabilities |
| 4. Workflows | 2 days | Enhanced workflows |
| 5. Frontend | 2 days | UI updates |
| 6. Testing | 2 days | Production ready |

**Total**: 12 days (2.5 weeks)

## Next Steps

1. Review and approve this plan
2. Set up development environment
3. Create feature branch
4. Begin Phase 1 implementation
5. Daily progress updates

## Questions & Concerns

- How to handle users without image generation permissions?
  - Fallback to text-only responses
  - Clear error messages
  
- How to prevent abuse?
  - Rate limiting per user
  - Content moderation
  - Cost thresholds
  
- What about existing workflows?
  - Backward compatible
  - Gradual migration
  - No breaking changes
