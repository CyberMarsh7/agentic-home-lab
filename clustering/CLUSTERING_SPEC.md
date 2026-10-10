# Clustering Backend Specification

## Overview
Unified memory pool across Pyramid, Victus, and Kali that allows:
1. Shared RAM access for all agents
2. Model management (load/unload on demand)
3. Request routing to appropriate device
4. Overflow storage on 2TB SSD

## Architecture

### Components

#### 1. Memory Manager (Redis/Cluster)
- Central memory broker
- Stores:
  - Available RAM on each device
  - Models currently loaded
  - Pending tasks
  - Coach validation rules
- Runs on: Victus (primary), Kali (backup)

#### 2. Model Manager
- Tracks models on 2TB SSD
- Manages loading/unloading into shared RAM
- Metadata:
  - Model size
  - Device requirements
  - Load time estimates
  - Performance profiles
- Implemented as: Python service on Victus + Pyramid

#### 3. Coach Agent
- Validates all requests before execution
- Prevents:
  - Prompt injection
  - Dangerous commands
  - Resource exhaustion
  - Unauthorized access
- Returns: APPROVE/REJECT with reason

#### 4. Task Router
- Receives requests from face
- Queries memory manager (available RAM, loaded models)
- Routes to appropriate device:
  - Victus GPU for heavy inference
  - Kali for security tasks
  - Pyramid for orchestration
- Returns results back to face

### Device Roles

#### Pyramid (Orchestrator)
- OpenClaw gateway
- Task router logic
- Face coordination
- Lightweight agent (voice, conversation)

#### Victus (Workhorse)
- Memory manager primary
- Model storage indexing
- Heavy inference (GPU)
- Redis primary instance

#### Kali (Security)
- Coach agent
- Network monitoring
- Request validation
- Memory manager backup

### Memory Flow

```
Request arrives at face
  ↓
Coach agent validates (APPROVE/REJECT)
  ↓
Task router checks memory manager
  ↓
If model not loaded: Load from 2TB SSD into shared RAM
  ↓
Execute on appropriate device
  ↓
Return results to face
  ↓
Unload model (if needed) to free RAM
```

## Implementation Strategy

### Phase 1: Foundation (In Progress)
- [ ] Set up shared memory backend (Redis)
- [ ] Create device discovery (each device registers available RAM)
- [ ] Implement model metadata system
- [ ] Create task router skeleton

### Phase 2: Agent Integration
- [ ] Connect OpenClaw agents to memory manager
- [ ] Implement coach agent validation
- [ ] Create model load/unload orchestration
- [ ] Test single task flow

### Phase 3: Optimization
- [ ] Monitor memory usage in real-time
- [ ] Optimize model loading order
- [ ] Implement task queuing
- [ ] Add failure recovery

### Phase 4: Face Integration
- [ ] Connect RasPad face to task router
- [ ] Test end-to-end conversation
- [ ] Add multi-camera support
- [ ] Deploy to production

## Key Files
- `clustering/backend/memory_manager.py` - Redis interface
- `clustering/backend/model_manager.py` - Model loading/unloading
- `clustering/backend/task_router.py` - Request routing
- `clustering/config/devices.json` - Device configuration
- `clustering/config/models.json` - Model metadata
