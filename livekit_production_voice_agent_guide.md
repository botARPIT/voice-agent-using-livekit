# Building Production-Grade Voice Agents with LiveKit
### A Complete Step-by-Step Engineering Guide

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Step 1 — Project Setup & Environment](#step-1--project-setup--environment)
3. [Step 2 — LiveKit Server & WebRTC Transport](#step-2--livekit-server--webrtc-transport)
4. [Step 3 — Choose Your Pipeline Architecture](#step-3--choose-your-pipeline-architecture)
5. [Step 4 — Speech-to-Text (STT)](#step-4--speech-to-text-stt)
6. [Step 5 — Large Language Model (LLM)](#step-5--large-language-model-llm)
7. [Step 6 — Text-to-Speech (TTS)](#step-6--text-to-speech-tts)
8. [Step 7 — Speech-to-Speech (Realtime) Models](#step-7--speech-to-speech-realtime-models)
9. [Step 8 — VAD & Turn Detection](#step-8--vad--turn-detection)
10. [Step 9 — Agent Session & Logic Structure](#step-9--agent-session--logic-structure)
11. [Step 10 — Tool Use & RAG Integration](#step-10--tool-use--rag-integration)
12. [Step 11 — Agent Server & Job Lifecycle](#step-11--agent-server--job-lifecycle)
13. [Step 12 — Multi-Agent Workflows & Handoffs](#step-12--multi-agent-workflows--handoffs)
14. [Step 13 — Telephony Integration (SIP)](#step-13--telephony-integration-sip)
15. [Step 14 — Frontend Integration](#step-14--frontend-integration)
16. [Step 15 — Deployment & Scaling](#step-15--deployment--scaling)
17. [Step 16 — Observability & Monitoring](#step-16--observability--monitoring)
18. [Pricing Reference — LiveKit Inference](#pricing-reference--livekit-inference)
19. [Production Checklist](#production-checklist)

---

## 1. Architecture Overview

LiveKit Agents is an open-source, realtime framework for building voice, video, and physical AI agents in Python or Node.js. Agents join LiveKit **Rooms** as full programmatic participants and communicate with users over **WebRTC** — the same protocol used in video calls — ensuring reliable, low-latency audio even on unstable mobile networks.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Device                          │
│          (Web/Mobile App or Phone via SIP/PSTN)             │
└───────────────────────┬─────────────────────────────────────┘
                        │  WebRTC (audio/video/data)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               LiveKit Server (SFU / Media Router)           │
│          LiveKit Cloud (managed) OR Self-hosted              │
│                                                             │
│   ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│   │ SIP Trunk│    │  LiveKit     │    │  Agent Dispatch  │  │
│   │(Telephony│    │  Rooms       │    │  & Load Balancer │  │
│   └──────────┘    └──────────────┘    └──────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │  HTTP/WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Server Process                      │
│            (your Python/Node.js agent code)                  │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  AgentSession                        │   │
│   │  ┌──────┐  ┌──────────┐  ┌──────┐  ┌──────────┐   │   │
│   │  │ STT  │→ │   LLM    │→ │ TTS  │→ │  Audio   │   │   │
│   │  │      │  │(+ Tools) │  │      │  │  Output  │   │   │
│   │  └──────┘  └──────────┘  └──────┘  └──────────┘   │   │
│   │  OR: Realtime Model (speech-to-speech, end-to-end)  │   │
│   └─────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │  HTTPS / WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                AI Model Providers                            │
│  STT: Deepgram, AssemblyAI, Cartesia, ElevenLabs             │
│  LLM: OpenAI, Gemini, DeepSeek, Qwen, xAI                   │
│  TTS: Cartesia, ElevenLabs, Deepgram, Rime, Inworld, xAI     │
│  Realtime: OpenAI Realtime, Gemini Live, Nova Sonic, xAI     │
└─────────────────────────────────────────────────────────────┘
```

### Core Components You Must Build or Configure

| Component | What it does | Required |
|-----------|-------------|----------|
| LiveKit Server | Routes WebRTC media between agent and users | Yes |
| Agent Server | Hosts your agent code; handles dispatch and job lifecycle | Yes |
| AgentSession | Orchestrates the STT→LLM→TTS pipeline per user session | Yes |
| STT Model | Converts user speech → text | Yes (unless using realtime model) |
| LLM | Generates agent responses | Yes |
| TTS Model | Converts agent text → speech | Yes (unless using realtime model) |
| VAD / Turn Detector | Detects when the user has finished speaking | Yes |
| Telephony (SIP) | Lets users call in from phones | Optional |
| Frontend SDK | Web/mobile client that connects users | Optional (phone replaces this) |

---

## Step 1 — Project Setup & Environment

### 1.1 Install the SDK

LiveKit Agents SDK supports **Python ≥ 3.9** and **Node.js ≥ 18**.

**Python (recommended for most production agents):**
```bash
# Use uv (fast) or pip
uv add "livekit-agents~=1.4"

# Install with specific plugins (only pay for what you use)
uv add "livekit-agents[openai,cartesia,deepgram,silero]~=1.4"
```

**Node.js:**
```bash
pnpm add "@livekit/agents@1.x"
pnpm add "@livekit/agents-plugin-openai@1.x"
pnpm add "@livekit/agents-plugin-cartesia@1.x"
```

### 1.2 Environment Variables

Create a `.env` file (never commit to version control):
```bash
# LiveKit Server credentials (from cloud.livekit.io or self-hosted)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxx
LIVEKIT_API_SECRET=your-secret

# Model provider API keys (only needed if NOT using LiveKit Inference)
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
CARTESIA_API_KEY=...
ELEVENLABS_API_KEY=...
```

> **Note:** If you use **LiveKit Inference** (models proxied through LiveKit Cloud), you only need `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET`. No per-provider keys required.

### 1.3 Minimal Agent Skeleton

```python
# agent.py
from livekit.agents import cli, WorkerOptions
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.agents import inference
from livekit import rtc

async def entrypoint(ctx):
    """Called when a new job (room) is dispatched to this agent."""
    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="en"),
        llm=inference.LLM(model="openai/gpt-4.1-mini"),
        tts=inference.TTS(model="cartesia/sonic-3", voice="<voice-id>"),
    )
    await session.start(
        room=ctx.room,
        agent=Agent(
            instructions="You are a helpful assistant. Keep responses concise.",
        ),
        room_input_options=RoomInputOptions(),
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

Run locally for development:
```bash
python agent.py dev
```

---

## Step 2 — LiveKit Server & WebRTC Transport

### 2.1 What the Server Does

The **LiveKit Server** is a Selective Forwarding Unit (SFU) — a media router that sits between your agent and users. It:
- Routes WebRTC audio/video streams between participants
- Manages rooms and participant lifecycles
- Dispatches agent jobs when users join rooms
- Handles NAT traversal, TURN relaying, and codec negotiation automatically

### 2.2 LiveKit Cloud (Recommended)

Sign up at **cloud.livekit.io**. You get:
- Globally distributed infrastructure (auto-selects nearest region)
- 1,000 free agent session minutes per month on the Build plan
- Built-in SIP/telephony support
- Observability: transcripts, traces, audio recordings

Your agent connects by registering with the server using `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET`.

### 2.3 Self-Hosting

If you need full data control, LiveKit Server is open source (Apache 2.0). You can run it on:
- **Virtual Machines**: Single-node Docker deployment
- **Kubernetes**: For horizontal scaling and high availability
- **Distributed multi-region**: For global low-latency deployments

Self-hosting requires separate deployment of the **SIP server** if you need telephony.

### 2.4 Rooms, Participants, and Tracks

The core primitives of the WebRTC transport layer:

| Primitive | Description |
|-----------|-------------|
| **Room** | A virtual conference space where agents and users meet. Each user session typically gets its own room. |
| **Participant** | Any entity in a room — a human user, your agent, or a SIP caller. |
| **Track** | A stream of audio or video published by a participant. Your agent subscribes to user audio tracks and publishes TTS audio tracks. |

**Access room context in your agent:**
```python
async def entrypoint(ctx):
    room: rtc.Room = ctx.room
    # room.name, room.participants, room.local_participant, etc.
```

### 2.5 Data Channels

Beyond audio/video, you can send arbitrary data between participants:
- **Text streams**: Real-time chat, transcription overlays
- **Byte streams**: Files, binary data
- **RPC calls**: Trigger agent actions from the frontend (e.g., "hang up now")
- **Data packets**: Low-latency custom events

---

## Step 3 — Choose Your Pipeline Architecture

This is the single most important architectural decision. LiveKit supports two approaches:

### Option A: STT → LLM → TTS Pipeline (Classic Pipeline)

**How it works:** Audio → Speech-to-Text → text transcript → LLM → text response → Text-to-Speech → audio output.

**Advantages:**
- Full control over each model (swap providers independently)
- Easy to inject business logic between stages
- Guaranteed access to transcripts at each step
- Scripted speech output works perfectly (use `session.say("...")`)
- Best for call centers, telephony, compliance-heavy use cases

**Disadvantages:**
- Higher latency (STT + LLM + TTS latency stacks up)
- Loses emotional nuance from voice (only text carries to LLM)

```python
session = AgentSession(
    stt=inference.STT(model="deepgram/nova-3"),
    llm=inference.LLM(model="openai/gpt-4.1-mini"),
    tts=inference.TTS(model="cartesia/sonic-3", voice="<id>"),
)
```

### Option B: Speech-to-Speech Realtime Model

**How it works:** Audio → Realtime Model → audio output directly. No STT or TTS needed.

**Advantages:**
- Lower latency (single model round-trip)
- Understands emotional tone, pace, and paralanguage
- More natural, expressive output speech
- Best for assistants, companions, creative use cases

**Disadvantages:**
- Transcripts are delayed or unavailable in real-time
- Cannot use `say()` for scripted speech
- Turn detection relies on model's built-in VAD (less controllable)
- Harder to inject business logic mid-pipeline

```python
from livekit.plugins import openai

session = AgentSession(
    llm=openai.realtime.RealtimeModel()
    # No stt or tts — the realtime model handles both
)
```

### Option C: Half-Cascade (Realtime Input + Custom TTS)

A hybrid approach: use a realtime model for **speech comprehension** but route its text output through a **custom TTS model** for **speech synthesis**. Best of both worlds in many cases.

```python
session = AgentSession(
    llm=openai.realtime.RealtimeModel(modalities=["text"]),  # text-only output
    tts=inference.TTS(model="cartesia/sonic-3", voice="<id>")
)
```

---

## Step 4 — Speech-to-Text (STT)

### 4.1 What STT Does

STT converts the user's incoming audio stream into text transcriptions that the LLM can process. For production, you want a **streaming** STT model that returns interim (partial) transcripts in real-time so the LLM can begin processing before the user finishes speaking.

### 4.2 Available STT Providers (via LiveKit Inference)

| Provider | Model | Languages | Price/min (Build) | Price/min (Scale) |
|----------|-------|-----------|-------------------|-------------------|
| Deepgram | Nova-3 | 44 languages | $0.0077 | $0.0065 |
| Deepgram | Nova-3 Medical | English | $0.0077 | $0.0065 |
| Deepgram | Nova-2 Phonecall | English | $0.0058 | $0.0047 |
| Deepgram | Flux | English | $0.0077 | $0.0065 |
| AssemblyAI | Universal-3 Pro Streaming | 6 languages | $0.0075 | $0.0075 |
| AssemblyAI | Universal-Streaming | English | $0.0025 | $0.0025 |
| Cartesia | Ink Whisper | 100 languages | $0.0030 | $0.0023 |
| ElevenLabs | Scribe v2 Realtime | 190 languages | $0.0105 | $0.0105 |

> **Recommendation:** Use **Deepgram Nova-3** for English-only apps (best accuracy/price), **Cartesia Ink Whisper** for multilingual (100 languages, very competitive pricing), or **ElevenLabs Scribe v2** for broadest language coverage.

### 4.3 Configuration

**Via LiveKit Inference (no API key needed):**
```python
stt=inference.STT(model="deepgram/nova-3", language="en")
# or shorthand:
stt="deepgram/nova-3:en"
```

**Via plugin (direct provider):**
```python
from livekit.plugins import deepgram
stt=deepgram.STT(model="nova-3", language="en")
```

### 4.4 Production Considerations for STT

- **Language detection**: For multilingual apps, use Nova-3 Multilingual or Ink Whisper and let the model auto-detect language.
- **Domain-specific models**: Use `nova-2-medical` or `nova-3-medical` for healthcare apps — significantly better accuracy for medical terminology.
- **Noise cancellation**: Enable Krisp noise cancellation on SIP inbound trunks for better STT accuracy in noisy call environments.
- **Interim transcripts**: Ensure your STT plugin supports streaming/interim results for minimal first-response latency.

---

## Step 5 — Large Language Model (LLM)

### 5.1 What the LLM Does

The LLM is the "brain" of your agent. It receives the transcribed text from STT, processes it in the context of the conversation history and system prompt, and generates the agent's reply as a text stream.

### 5.2 Available LLMs (via LiveKit Inference)

| Model | Provider | Input ($/M tokens) | Output ($/M tokens) | Best For |
|-------|----------|--------------------|---------------------|----------|
| GPT-4.1 nano | OpenAI | $0.10 | $0.40 | Low-cost, high-volume |
| GPT-4.1 mini | OpenAI | $0.40 | $1.60 | Best balance of cost/quality |
| GPT-4.1 | OpenAI | $2.00 | $8.00 | Complex reasoning |
| GPT-5 mini | OpenAI | $0.25 | $2.00 | Next-gen quality, low cost |
| GPT-5 | OpenAI | $1.25 | $10.00 | Frontier reasoning |
| Gemini 2.5 Flash Lite | Google | $0.10 | $0.40 | Ultra-cheap, fast |
| Gemini 2.5 Flash | Google | $0.30 | $2.50 | Great multilingual support |
| Gemini 2.5 Pro | Google | $2.50 | $15.00 | Best Google model |
| DeepSeek V3 | Baseten | $0.77 | $0.77 | Open-weights, competitive |
| Kimi K2.5 | Moonshot | $0.60 | $2.50 | Strong agentic/tool use |

### 5.3 Configuration

```python
# Via LiveKit Inference
llm=inference.LLM(model="openai/gpt-4.1-mini")

# Via OpenAI plugin directly (Responses API, recommended)
from livekit.plugins import openai
llm=openai.responses.LLM(model="gpt-4.1-mini")

# OpenAI-compatible endpoint (e.g., Groq, Ollama, custom)
llm=openai.LLM(
    model="llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)
```

### 5.4 System Prompt & Instructions

The system prompt is your primary lever for controlling agent behavior:
```python
agent = Agent(
    instructions="""
    You are a friendly customer service agent for Acme Corp.
    Keep all responses under 3 sentences unless asked for detail.
    Always confirm the user's name before accessing their account.
    Never discuss competitor products.
    If asked about billing, transfer to billing department.
    """,
)
```

See the LiveKit [Prompting Guide](https://docs.livekit.io/agents/start/prompting/) for voice-specific prompting techniques (conciseness, no markdown, conversational phrasing).

### 5.5 Production Considerations for LLM

- **Latency vs. quality trade-off**: GPT-4.1 mini and Gemini 2.5 Flash offer the best speed/quality ratio for conversational voice.
- **Prompt caching**: Models with cached input pricing (all OpenAI/Google models) reduce cost significantly for long system prompts — design your system prompt to be large and stable, not dynamic.
- **Context window**: Keep conversation history manageable. For long calls, summarize older turns rather than passing everything.
- **Streaming**: Always use streaming output so TTS can begin speaking before the LLM finishes generating. The framework handles this automatically.

---

## Step 6 — Text-to-Speech (TTS)

### 6.1 What TTS Does

TTS converts the LLM's text response into audio that is streamed back to the user as speech. Modern TTS models can produce natural, expressive voices with sub-300ms latency.

### 6.2 Available TTS Providers (via LiveKit Inference)

| Provider | Model | Price/M chars (Build) | Price/M chars (Scale) | Languages |
|----------|-------|-----------------------|-----------------------|-----------|
| Cartesia | Sonic 3 | $50.00 | $37.50 | 50+ |
| Cartesia | Sonic Turbo | $50.00 | $37.50 | 14 |
| Deepgram | Aura-2 | $30.00 | $27.00 | 12 languages |
| ElevenLabs | Flash v2.5 | $150.00 | $60.00 | 30+ |
| ElevenLabs | Turbo v2.5 | $150.00 | $60.00 | 30+ |
| ElevenLabs | Multilingual v2 | $300.00 | $120.00 | 29 |
| Inworld | TTS 1.5 Mini | $5.00 | $5.00 | 12 |
| Inworld | TTS 1.5 Max | $10.00 | $10.00 | 12 |
| Rime | Mist v2 | $30.00 | $20.00 | 4 |
| xAI | TTS-1 | — | — | 20+ |

> **Recommendation:** **Cartesia Sonic 3** is the top choice for voice agents — lowest latency, great expressiveness, broad language support, and competitive pricing. **Deepgram Aura-2** is the budget option. **ElevenLabs** for premium voice cloning quality.

### 6.3 Configuration

```python
# Via LiveKit Inference (voice ID is Cartesia's voice UUID)
tts=inference.TTS(
    model="cartesia/sonic-3",
    voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"  # Cartesia voice ID
)
# Shorthand: "cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"

# Via plugin directly
from livekit.plugins import cartesia
tts=cartesia.TTS(model="sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc")
```

### 6.4 Scripted Speech

For announcements, greetings, or required disclosures, you can directly speak text without going through the LLM:
```python
await session.say("Welcome to Acme Corp. Your call may be recorded.")
await session.say("Please hold while I look that up.", allow_interruptions=False)
```

### 6.5 Production Considerations for TTS

- **Voice selection**: Match voice personality to your brand. Test voices at Cartesia's voice library or ElevenLabs voice lab.
- **Voice cloning**: For branded experiences, ElevenLabs and Cartesia support custom voice cloning.
- **Streaming**: The framework pipes LLM token output directly to TTS as it streams, minimizing time-to-first-audio.
- **Pronunciation control**: Use Pipeline Nodes to intercept TTS input and fix pronunciations (acronyms, brand names, etc.).

---

## Step 7 — Speech-to-Speech (Realtime) Models

### 7.1 Overview

Realtime models consume and produce speech directly, without a separate STT and TTS step. They understand emotional context, tone, and paralanguage in ways that text-based pipelines cannot.

### 7.2 Supported Realtime Model Providers

| Provider | Model | Python | Node.js | Notes |
|----------|-------|--------|---------|-------|
| OpenAI | Realtime API (GPT-4o) | ✓ | ✓ | Most mature; best tool use |
| Google | Gemini Live API | ✓ | ✓ | Strong multilingual |
| Azure OpenAI | Realtime API | ✓ | ✓ | Enterprise/compliance |
| Amazon | Nova Sonic | ✓ | — | AWS-native |
| Ultravox | Realtime | ✓ | — | Open-source model |
| xAI | Grok Voice Agent API | ✓ | — | New, emerging |

**Yes — LiveKit fully supports speech-to-speech models.** This is a first-class feature of the framework.

### 7.3 Using OpenAI Realtime API

```python
from livekit.plugins import openai

session = AgentSession(
    llm=openai.realtime.RealtimeModel(
        model="gpt-4o-realtime-preview",
        voice="alloy",  # OpenAI voice name
    )
)
```

### 7.4 Using Gemini Live API

```python
from livekit.plugins import google

session = AgentSession(
    llm=google.beta.realtime.RealtimeModel(
        model="gemini-2.0-flash-exp",
        voice="Puck",
    )
)
```

### 7.5 Half-Cascade: Realtime Input + Custom TTS

Use a realtime model for speech comprehension but your own TTS for output:
```python
session = AgentSession(
    llm=openai.realtime.RealtimeModel(
        modalities=["text"],  # Text-only output from realtime model
    ),
    tts=inference.TTS(model="cartesia/sonic-3", voice="<id>")
)
```
This pattern is ideal when you need custom voice branding but want the emotional understanding of a realtime model.

### 7.6 Limitations of Realtime Models

- **No interim transcriptions**: User speech transcripts arrive after the agent's response, not during.
- **No scripted output**: You cannot call `session.say("exact text")` and guarantee it's spoken verbatim.
- **Conversation history**: Only text-format history can be loaded; limits emotional context on re-connect.
- **Turn detection**: Rely on the model's built-in VAD; adding a separate STT plugin is needed if you want LiveKit's turn detector.

### 7.7 Realtime Model Pricing

Realtime models are billed directly by their provider (not through LiveKit Inference currently):

| Provider | Input Audio | Output Audio |
|----------|-------------|--------------|
| OpenAI Realtime (GPT-4o) | $100/M tokens (~$0.06/min audio) | $200/M tokens (~$0.24/min audio) |
| Gemini Live (2.0 Flash) | ~$0.70/M audio tokens | ~$0.70/M audio tokens |

> **Cost note**: Realtime speech-to-speech models are significantly more expensive per minute than STT+LLM+TTS pipelines. Use them when the quality justifies the cost.

---

## Step 8 — VAD & Turn Detection

### 8.1 What Turn Detection Does

Turn detection determines *when the user has finished speaking* — a deceptively hard problem. Detect too early: agent interrupts the user. Detect too late: awkward silence. Getting this right is critical for natural conversation.

### 8.2 LiveKit's Turn Detection Stack

LiveKit uses a multi-layer approach:
1. **Voice Activity Detection (VAD)**: Silero VAD detects speech vs. silence at the audio level.
2. **Turn Detector Model**: A custom LiveKit ML model that combines VAD + semantic context from interim transcripts to predict when a turn is truly complete — not just a mid-sentence pause.
3. **Realtime model VAD**: When using realtime models, the model's built-in VAD is used instead.

### 8.3 Configuration

```python
from livekit.agents import TurnDetectionMode
from livekit.plugins import silero

session = AgentSession(
    # ...stt, llm, tts...
    # Turn detection is automatic — the framework picks the best strategy
    # You can override:
    turn_detection=TurnDetectionMode.VAD_ONLY,  # Use only audio VAD
    # or leave as default (LiveKit's turn detector model)
)
```

### 8.4 Interruptions

Interruptions are automatically handled — if a user starts speaking while the agent is talking, the agent stops and listens. You can configure this behavior:

```python
session = AgentSession(
    allow_interruptions=True,  # default: True
    min_interruption_duration=0.5,  # seconds of speech before interrupting
)
```

### 8.5 Push-to-Talk

For noisy environments or specific UX patterns, you can disable automatic turn detection and require explicit signals:
```python
# Frontend sends a data message to start/stop agent listening
# See: https://docs.livekit.io/agents/logic/turns/
```

---

## Step 9 — Agent Session & Logic Structure

### 9.1 AgentSession: The Main Orchestrator

`AgentSession` is the central class that wires together all the models and manages the conversation flow. It handles:
- Audio input collection from the room
- Running audio through the STT→LLM→TTS pipeline (or realtime model)
- Delivering audio output back to the room
- Managing conversation history
- Dispatching tool calls

### 9.2 Agent Sessions

Each user joining a room gets their own `AgentSession`. The session manages:
- The active participant the agent is listening to
- The current conversation context and history
- Model configurations and lifecycle

### 9.3 Tasks

Tasks are focused, reusable units that take temporary control of the conversation to accomplish a specific objective and return a typed result:

```python
from livekit.agents import AgentTask

async def collect_consent(session: AgentSession) -> bool:
    """A task that collects explicit consent from the user."""
    task = AgentTask(
        instructions="Ask the user if they consent to recording. Return True if yes, False if no.",
        result_schema=bool,
    )
    result = await session.run_task(task)
    return result
```

Use tasks for: consent collection, form filling, structured data capture, multi-step authentication.

### 9.4 Workflows

Workflows model complex, multi-phase conversations with multiple agents or conversation states:

```python
# Example: Customer service workflow
# Phase 1: Greeting agent identifies intent
# Phase 2: Route to billing, technical, or general agent
# Phase 3: Escalate to human if needed

from livekit.agents import Workflow

workflow = Workflow([
    GreetingAgent,    # Identifies user intent
    BillingAgent,     # Handles billing questions
    TechSupportAgent, # Handles technical issues
])
```

### 9.5 Pipeline Nodes & Hooks

Pipeline nodes let you intercept and modify data at any point in the pipeline:

```python
from livekit.agents import PipelineNode

@session.on("before_tts")
async def fix_pronunciation(text: str) -> str:
    """Fix pronunciation of brand names before TTS."""
    return text.replace("Acme Corp", "Ak-mee Corp")

@session.on("after_stt")
async def log_transcript(transcript: str):
    """Log all user speech for analytics."""
    await send_to_analytics(transcript)
```

### 9.6 External Data & RAG

Connect your agent to external data sources for Retrieval-Augmented Generation:

```python
@function_tool
async def search_knowledge_base(query: str) -> str:
    """Search the company knowledge base for relevant information."""
    results = await vector_db.search(query, top_k=3)
    return "\n".join(r.text for r in results)

agent = Agent(
    instructions="Use the search tool when you need specific company information.",
    tools=[search_knowledge_base],
)
```

---

## Step 10 — Tool Use & RAG Integration

### 10.1 Defining Tools

Tools are Python functions the LLM can call during a conversation. They're how your agent takes real-world actions:

```python
from livekit.agents import function_tool, AgentSession
import httpx

@function_tool
async def get_account_balance(customer_id: str) -> dict:
    """
    Look up a customer's account balance.
    
    Args:
        customer_id: The customer's account ID (format: CUST-XXXXX)
    
    Returns a dict with 'balance' and 'currency' fields.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.yourcompany.com/accounts/{customer_id}")
        return response.json()

@function_tool  
async def create_support_ticket(
    subject: str, 
    description: str, 
    priority: str = "medium"
) -> str:
    """Create a support ticket and return the ticket ID."""
    ticket = await helpdesk.create(subject=subject, description=description, priority=priority)
    return f"Ticket {ticket.id} created successfully."

agent = Agent(
    instructions="You are a customer service agent. Use tools to look up account information and create tickets.",
    tools=[get_account_balance, create_support_ticket],
)
```

### 10.2 Forwarding Tool Calls to Frontend

You can expose tool calls to the frontend for UI updates:
```python
@function_tool(forward_to_client=True)
async def show_product_card(product_id: str):
    """Tell the frontend to display a product card."""
    # Frontend handles this via data channel
    pass
```

### 10.3 RAG Pattern

```python
from livekit.agents import function_tool
from your_vector_db import ChromaDB  # or Pinecone, Weaviate, etc.

db = ChromaDB()

@function_tool
async def search_docs(query: str) -> str:
    """Search internal documentation for relevant information."""
    results = db.query(query_texts=[query], n_results=3)
    return "\n---\n".join(results["documents"][0])

# Preload context at session start
async def entrypoint(ctx):
    # Load user profile into initial context
    user_data = await fetch_user_profile(ctx.room.metadata)
    
    session = AgentSession(
        # ...models...
        initial_context=f"User profile: {user_data}"
    )
    agent = Agent(
        instructions="Use search_docs to answer questions from company documentation.",
        tools=[search_docs],
    )
    await session.start(room=ctx.room, agent=agent)
```

---

## Step 11 — Agent Server & Job Lifecycle

### 11.1 How Agent Servers Work

When your agent code starts, it:
1. **Registers** with the LiveKit server as an "agent server" process
2. **Waits** for dispatch requests (new rooms to join)
3. On dispatch: **boots a job subprocess** that joins the room
4. The job subprocess runs your `entrypoint` function
5. When the room ends, the job exits gracefully

### 11.2 Startup Modes

```bash
# Development mode — watch for file changes, verbose logging
python agent.py dev

# Production mode — connects to LiveKit server and waits for jobs
python agent.py start

# Console mode — join a specific room for debugging
python agent.py connect --room my-room-name
```

### 11.3 WorkerOptions Configuration

```python
from livekit.agents import cli, WorkerOptions

cli.run_app(
    WorkerOptions(
        entrypoint_fnc=entrypoint,
        
        # Pre-warm: load models before first job arrives (reduces cold start)
        prewarm_fnc=prewarm,
        
        # Number of CPU workers (default: number of CPUs)
        num_idle_processes=2,
        
        # Auto-dispatch to all new rooms (default: True)
        # Set to False for explicit dispatch only
        auto_subscribe=True,
        
        # Agent name for explicit dispatch
        agent_name="customer-service-agent",
    )
)

async def prewarm(proc):
    """Pre-load models when the worker process starts."""
    proc.userdata["vad"] = await silero.VAD.load()
```

### 11.4 Agent Dispatch

By default, your agent is dispatched to every new room. For more control:

**Explicit dispatch** — only join rooms when explicitly requested via the API:
```python
WorkerOptions(
    entrypoint_fnc=entrypoint,
    agent_name="billing-agent",  # Named agent for explicit dispatch
)
```

Then from your backend:
```python
from livekit.api import LiveKitAPI, CreateAgentDispatchRequest

lk = LiveKitAPI(url, api_key, api_secret)
await lk.agent_dispatch.create_dispatch(
    CreateAgentDispatchRequest(
        room_name="user-room-123",
        agent_name="billing-agent",
        metadata='{"user_id": "12345"}'
    )
)
```

### 11.5 Graceful Shutdown

The agent server supports graceful shutdown — it stops accepting new jobs and waits for active sessions to complete before exiting. This ensures no calls are dropped during deployments.

---

## Step 12 — Multi-Agent Workflows & Handoffs

### 12.1 Why Multi-Agent

Complex voice applications benefit from specialized agents:
- A **greeter agent** identifies intent and routes the call
- A **billing agent** handles payment questions with specific tools/permissions
- A **technical support agent** handles product issues
- A **human escalation agent** initiates warm transfer to a live agent

### 12.2 Defining Multiple Agents

```python
from livekit.agents import Agent

greeter = Agent(
    name="greeter",
    instructions="Greet the caller and determine if they need billing, technical support, or general help. Then hand off appropriately.",
)

billing_agent = Agent(
    name="billing",
    instructions="You specialize in billing questions. You have access to account and payment tools.",
    tools=[get_account, process_payment, create_billing_ticket],
)

tech_agent = Agent(
    name="tech_support",
    instructions="You handle technical support. Diagnose issues and create support tickets.",
    tools=[diagnose_issue, create_ticket, escalate_to_engineer],
)
```

### 12.3 Handoffs

```python
from livekit.agents import AgentHandoff

@function_tool
async def transfer_to_billing() -> AgentHandoff:
    """Transfer this caller to the billing department."""
    return AgentHandoff(agent=billing_agent)

@function_tool
async def transfer_to_tech() -> AgentHandoff:
    """Transfer this caller to technical support."""
    return AgentHandoff(agent=tech_agent)

# Add handoff tools to the greeter
greeter_with_handoffs = Agent(
    name="greeter",
    instructions="Greet and route callers appropriately.",
    tools=[transfer_to_billing, transfer_to_tech],
)
```

### 12.4 Context Preservation During Handoffs

Conversation history is automatically passed to the new agent. You can also pass custom metadata:
```python
return AgentHandoff(
    agent=billing_agent,
    handoff_instructions="User is asking about invoice #INV-12345 from last month."
)
```

---

## Step 13 — Telephony Integration (SIP)

### 13.1 Overview

LiveKit's telephony system lets callers use regular phone numbers to interact with your AI agent. This is powered by the SIP (Session Initiation Protocol) standard.

### 13.2 Architecture

```
Caller's Phone
      │
      │ PSTN (regular phone network)
      ▼
 Phone Number (LiveKit Phone Numbers or Twilio/Telnyx/etc.)
      │
      │ SIP trunk
      ▼
 LiveKit SIP Service
      │
      │ Creates SIP participant in room
      ▼
 LiveKit Room + Your Agent
```

### 13.3 Components

**Trunks** bridge your SIP provider to LiveKit:
- **Inbound trunk**: Receives incoming calls; restrict to specific IP ranges or numbers for security
- **Outbound trunk**: Makes outgoing calls

**Dispatch Rules** control how inbound calls are routed to rooms:
- Route all callers to the same room (e.g., a queue)
- Give each caller a unique room (most common for AI agents)
- Route based on PIN codes for IVR-style menus

**SIP Participants** are just regular LiveKit participants with extra telephony metadata (caller ID, etc.).

### 13.4 Setting Up Inbound Calls

**Step 1**: Buy a phone number (LiveKit Phone Numbers) or configure a SIP trunk with Twilio/Telnyx/Exotel/Plivo.

**Step 2**: Create an inbound SIP trunk via the API:
```python
from livekit.api import LiveKitAPI, SIPTrunkInfo

lk = LiveKitAPI(url, api_key, api_secret)
trunk = await lk.sip.create_sip_inbound_trunk(
    SIPInboundTrunkInfo(
        name="Main Inbound Trunk",
        numbers=["+15551234567"],
        krisp_enabled=True,  # Enable noise cancellation
    )
)
```

**Step 3**: Create a dispatch rule:
```python
await lk.sip.create_sip_dispatch_rule(
    CreateSIPDispatchRuleRequest(
        rule=SIPDispatchRule(
            dispatch_rule_individual=SIPDispatchRuleIndividual(
                room_prefix="call-",
            )
        ),
        trunk_ids=[trunk.sip_trunk_id],
    )
)
```

**Step 4**: Configure your agent to handle telephony sessions with appropriate greetings:
```python
async def entrypoint(ctx):
    # Detect if this is a phone call
    is_phone_call = ctx.room.metadata and "sip" in ctx.room.metadata
    
    session = AgentSession(...)
    agent = Agent(
        instructions="""
        You are answering a phone call. Keep responses brief.
        Always identify yourself at the start of the call.
        Speak clearly and at a moderate pace.
        """
    )
    
    if is_phone_call:
        await session.say("Hello, thank you for calling Acme Corp. How can I help you today?")
    
    await session.start(room=ctx.room, agent=agent)
```

### 13.5 Outbound Calls

```python
from livekit.api import CreateSIPParticipantRequest

# Create a room first, then add a SIP caller
await lk.sip.create_sip_participant(
    CreateSIPParticipantRequest(
        room_name="outbound-room-123",
        sip_trunk_id=outbound_trunk.sip_trunk_id,
        sip_call_to="+15559876543",  # Number to dial
        participant_name="John Smith",
        krisp_enabled=True,
    )
)
```

### 13.6 Supported SIP Features

| Feature | Supported |
|---------|-----------|
| SIP over UDP/TCP/TLS | ✓ |
| DTMF tones | ✓ |
| Cold transfer (REFER) | ✓ |
| Warm transfer | ✓ |
| Caller ID | ✓ |
| SRTP (encrypted media) | ✓ |
| HD Voice | ✓ |
| Noise cancellation (Krisp) | ✓ |
| SIP Registration | ✗ |
| Video over SIP | ✗ |

### 13.7 Tested SIP Providers

LiveKit SIP has been tested with: **Twilio, Telnyx, Exotel, Plivo, Wavix**. It's designed to work with any standards-compliant SIP provider.

---

## Step 14 — Frontend Integration

### 14.1 WebRTC Frontend Options

Users can connect to your agent via a web or mobile app using LiveKit's client SDKs:

| Platform | SDK | Notes |
|----------|-----|-------|
| Web (React) | `@livekit/components-react` | Pre-built UI components |
| Web (vanilla JS) | `livekit-client` | Full control |
| iOS/macOS | Swift SDK | Native Apple |
| Android | Kotlin SDK | Native Android |
| React Native | `@livekit/react-native` | Cross-platform mobile |
| Flutter | `livekit_client` | Cross-platform |

### 14.2 Token Generation

Your backend generates access tokens for users to connect to rooms:
```python
from livekit import api

def create_token(room_name: str, participant_name: str) -> str:
    token = api.AccessToken(api_key, api_secret)
    token.with_identity(participant_name)
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
    ))
    return token.to_jwt()
```

### 14.3 Minimal React Frontend

```jsx
import { LiveKitRoom, useVoiceAssistant, BarVisualizer } from "@livekit/components-react";

function App() {
  const token = await fetchTokenFromYourBackend();
  
  return (
    <LiveKitRoom
      serverUrl={process.env.LIVEKIT_URL}
      token={token}
      connect={true}
    >
      <VoiceAgent />
    </LiveKitRoom>
  );
}

function VoiceAgent() {
  const { state, audioTrack } = useVoiceAssistant();
  
  return (
    <div>
      <p>Agent is: {state}</p>  {/* listening / thinking / speaking */}
      <BarVisualizer state={state} trackRef={audioTrack} />
    </div>
  );
}
```

---

## Step 15 — Deployment & Scaling

### 15.1 Deployment Options

| Option | Best For | Scaling |
|--------|----------|---------|
| **LiveKit Cloud** | Most teams; production-ready immediately | Automatic |
| **Custom VM/Bare Metal** | Cost optimization at very high scale | Manual |
| **Kubernetes** | Teams with existing K8s infrastructure | HPA-based |

### 15.2 Deploying to LiveKit Cloud

LiveKit Cloud provides a managed deployment environment with automatic scaling and built-in observability.

**Step 1**: Install the LiveKit CLI:
```bash
curl -sSL https://get.livekit.io/cli | bash
lk cloud auth
```

**Step 2**: Create a `livekit.yaml` deployment config:
```yaml
name: my-voice-agent
version: "1.0.0"
runtime: python3.11

build:
  dockerfile: Dockerfile

env:
  - OPENAI_API_KEY
  - DEEPGRAM_API_KEY
```

**Step 3**: Deploy:
```bash
lk cloud agent deploy
```

This builds your Docker image, pushes it to LiveKit Cloud, and starts your agent servers. LiveKit Cloud handles:
- Auto-scaling based on concurrent sessions
- Load balancing across agent server instances
- Graceful rolling deployments
- Global distribution (deploy to the region nearest your users)

### 15.3 Dockerfile for Production

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev deps)
RUN uv sync --frozen --no-dev

# Copy agent code
COPY agent.py .

# Start the agent in production mode
CMD ["uv", "run", "python", "agent.py", "start"]
```

### 15.4 Self-Hosted Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voice-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: voice-agent
  template:
    metadata:
      labels:
        app: voice-agent
    spec:
      containers:
      - name: agent
        image: your-registry/voice-agent:latest
        env:
        - name: LIVEKIT_URL
          valueFrom:
            secretKeyRef:
              name: livekit-secrets
              key: url
        - name: LIVEKIT_API_KEY
          valueFrom:
            secretKeyRef:
              name: livekit-secrets
              key: api_key
        - name: LIVEKIT_API_SECRET
          valueFrom:
            secretKeyRef:
              name: livekit-secrets
              key: api_secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1"
```

### 15.5 Scaling Considerations

- Each agent job (room) runs in its own subprocess. CPU/memory scales with concurrent sessions.
- LiveKit's agent server automatically load-balances new jobs across running instances.
- For telephony-heavy workloads, ensure the SIP service has sufficient capacity.
- Pre-warm workers with `prewarm_fnc` to eliminate cold starts for new sessions.

### 15.6 Secrets Management

Never hardcode API keys. Use:
- **LiveKit Cloud**: Built-in secrets manager in the CLI (`lk cloud secrets set KEY VALUE`)
- **Kubernetes**: Kubernetes Secrets or external secrets operators (Vault, AWS Secrets Manager)
- **Local dev**: `.env` files loaded with `python-dotenv`

---

## Step 16 — Observability & Monitoring

### 16.1 LiveKit Cloud Insights

LiveKit Cloud provides built-in observability for every session:
- **Transcripts**: Full conversation transcripts with timestamps
- **Traces**: Pipeline execution traces showing latency at each step (STT, LLM, TTS)
- **Audio recordings**: Recordings of each session (opt-in)
- **Logs**: Agent server logs with session context

Access via the LiveKit Cloud dashboard or the Analytics API.

### 16.2 Data Hooks

For custom analytics pipelines, data hooks let you stream session data to your own systems:
```python
# In your entrypoint, register hooks
@ctx.room.on("transcript_received")
async def on_transcript(transcript):
    await your_analytics_system.log(
        session_id=ctx.job.id,
        speaker=transcript.speaker,
        text=transcript.text,
        timestamp=transcript.timestamp,
    )
```

### 16.3 Error Handling

```python
from livekit.agents import AgentSession

session = AgentSession(...)

@session.on("error")
async def on_error(error: Exception):
    logger.error(f"Session error: {error}", exc_info=True)
    await alert_system.notify(f"Agent session {ctx.job.id} error: {error}")
    # Optionally: say something to the user
    await session.say("I'm experiencing a technical issue. Please try again.")
```

### 16.4 Key Metrics to Track

| Metric | Target | Notes |
|--------|--------|-------|
| Time-to-first-audio | < 1.0s | From user finishing speech to agent starting speech |
| STT latency | < 200ms | Interim results reduce perceived latency |
| LLM first token latency | < 500ms | Time to first token from LLM |
| TTS first audio chunk | < 150ms | Cartesia Sonic 3 achieves ~80ms |
| Interruption response time | < 300ms | How fast agent stops when user interrupts |
| Session success rate | > 99% | Sessions completing without errors |

---

## Pricing Reference — LiveKit Inference

All prices are in addition to LiveKit's platform/session pricing (1,000 free minutes/month on Build plan).

### Platform Plans

| Feature | Build ($0/mo) | Ship ($50/mo) | Scale ($500/mo) |
|---------|--------------|---------------|-----------------|
| Free credits | $2.50 | $5.00 | $50.00 |
| Inference concurrency | 5 | 20 | 50 |
| Coverage | ~50 min | ~100 min | ~1,000 min |

### LLM Pricing (per million tokens)

| Model | Input | Cached Input | Output |
|-------|-------|--------------|--------|
| GPT-4.1 nano | $0.10 | $0.025 | $0.40 |
| GPT-4.1 mini | $0.40 | $0.10 | $1.60 |
| GPT-4.1 | $2.00 | $0.50 | $8.00 |
| GPT-5 mini | $0.25 | $0.025 | $2.00 |
| GPT-5 | $1.25 | $0.125 | $10.00 |
| Gemini 2.5 Flash Lite | $0.10 | $0.01 | $0.40 |
| Gemini 2.5 Flash | $0.30 | $0.03 | $2.50 |
| Gemini 2.5 Pro | $2.50 | $0.25 | $15.00 |
| DeepSeek V3 | $0.77 | N/A | $0.77 |

### STT Pricing (per minute of audio)

| Provider & Model | Build/Ship | Scale |
|------------------|-----------|-------|
| AssemblyAI Universal-Streaming | $0.0025 | $0.0025 |
| Cartesia Ink Whisper | $0.0030 | $0.0023 |
| Deepgram Nova-2 | $0.0058 | $0.0047 |
| Deepgram Nova-3 | $0.0077 | $0.0065 |
| AssemblyAI U3 Pro Streaming | $0.0075 | $0.0075 |
| ElevenLabs Scribe v2 Realtime | $0.0105 | $0.0105 |

### TTS Pricing (per million characters)

| Provider & Model | Build/Ship | Scale |
|------------------|-----------|-------|
| Inworld TTS 1.5 Mini | $5.00 | $5.00 |
| Inworld TTS 1.5 Max | $10.00 | $10.00 |
| Deepgram Aura-2 | $30.00 | $27.00 |
| Rime Mist v2 | $30.00 | $20.00 |
| Cartesia Sonic 3 | $50.00 | $37.50 |
| ElevenLabs Flash v2.5 | $150.00 | $60.00 |
| ElevenLabs Multilingual v2 | $300.00 | $120.00 |

### Estimated Cost per Conversation (10-minute call)

Using the recommended stack (Deepgram Nova-3 STT + GPT-4.1 mini LLM + Cartesia Sonic 3 TTS):
- STT: 10 min × $0.0077 = **$0.077**
- LLM: ~1,500 tokens in + ~800 out = **~$0.002**
- TTS: ~1,000 chars output = **~$0.05**
- **Total: ~$0.13 per 10-minute call** (Build plan)

On Scale plan: **~$0.10 per 10-minute call**

---

## Production Checklist

Use this before going live:

### Environment & Security
- [ ] All API keys stored in secrets manager (not in code or `.env` in production)
- [ ] LiveKit API secret rotated from development key
- [ ] CORS and token scopes configured correctly
- [ ] Rate limiting on your token generation endpoint

### Agent Quality
- [ ] System prompt tested for edge cases (confused users, off-topic, abuse)
- [ ] Tool error handling in place (API timeouts, bad responses)
- [ ] Agent tested with real phone calls if using telephony
- [ ] Turn detection tuned for your specific use case (fast speech, accents, noisy environments)

### Infrastructure
- [ ] Agent server running with minimum 2 replicas (no single point of failure)
- [ ] Health checks configured for Kubernetes/load balancer
- [ ] `prewarm_fnc` loading models to eliminate cold starts
- [ ] Graceful shutdown configured (no dropped calls on deploy)
- [ ] Memory/CPU limits set based on load testing

### Telephony (if applicable)
- [ ] SIP trunk tested end-to-end with real phone
- [ ] Noise cancellation (Krisp) enabled on inbound trunks
- [ ] Dispatch rules verified (correct room routing)
- [ ] DTMF handling implemented if needed
- [ ] Outbound caller ID configured

### Observability
- [ ] Session transcripts enabled and accessible
- [ ] Error alerts configured (PagerDuty, Slack, etc.)
- [ ] Latency monitoring set up (time-to-first-audio dashboard)
- [ ] Cost monitoring active (especially for LLM usage)
- [ ] Audio recordings enabled for QA sampling

### Testing
- [ ] Load tested at 2x expected peak concurrency
- [ ] Interruption handling tested (user interrupting agent mid-sentence)
- [ ] Network degradation tested (user on mobile/slow connection)
- [ ] Tool failure scenarios tested
- [ ] Long conversation tested (30+ minute sessions)

---

*Guide based on LiveKit Agents framework v1.4+, as documented at docs.livekit.io. Pricing current as of March 2026 — always verify latest prices at livekit.io/pricing/inference.*
