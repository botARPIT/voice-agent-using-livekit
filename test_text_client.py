#!/usr/bin/env python3
"""
Simple text-based test client for the voice agent.
Connects to the agent via LiveKit and allows text-based interaction.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from livekit import api, rtc
from livekit.agents import AgentSession, Agent

# Load environment variables
load_dotenv()


async def text_interaction():
    """Run text-based interaction with the agent."""
    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not all([url, api_key, api_secret]):
        print("Error: Please set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET in .env")
        return

    # Create room name
    room_name = "test-text-room-001"

    # Create access token
    token = api.AccessToken(api_key, api_secret)
    token.with_identity("text-user")
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
    ))
    token_str = token.to_jwt()

    print("=" * 60)
    print("Real Estate Voice Agent - Text Test Client")
    print("=" * 60)
    print(f"Connecting to room: {room_name}")
    print()

    # Connect to room
    room = rtc.Room()

    connected = asyncio.Event()
    agent_joined = asyncio.Event()

    @room.on("connected")
    def on_connected():
        print("✓ Connected to LiveKit room")
        connected.set()

    @room.on("disconnected")
    def on_disconnected():
        print("Disconnected from room")

    @room.on("participant_connected")
    def on_participant_connected(participant):
        print(f"✓ Agent joined: {participant.identity}")
        agent_joined.set()

    @room.on("data_received")
    def on_data_received(data, participant):
        """Receive text messages from agent."""
        if data.data:
            message = data.data.decode('utf-8')
            print(f"\n🤖 Agent: {message}\n")

    print(f"Connecting to {url}...")
    await room.connect(url, token_str)

    # Wait for connection
    await asyncio.wait_for(connected.wait(), timeout=10)
    print("Waiting for agent to join...")

    # Wait for agent to join
    try:
        await asyncio.wait_for(agent_joined.wait(), timeout=30)
    except asyncio.TimeoutError:
        print("⚠ Agent didn't join. Make sure the agent server is running.")
        print("Run: ./run.sh")
        await room.disconnect()
        return

    print()
    print("=" * 60)
    print("Type your messages below (or 'quit' to exit):")
    print("=" * 60)
    print()

    # Interactive loop
    while True:
        try:
            # Get user input
            message = input("You: ").strip()

            if message.lower() in ['quit', 'exit', 'q']:
                print("\nDisconnecting...")
                break

            if not message:
                continue

            # Send message to agent via data channel
            await room.local_participant.publish_data(
                message.encode('utf-8'),
                topic="user_message"
            )

        except KeyboardInterrupt:
            print("\nDisconnecting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

    await room.disconnect()
    print("Disconnected.")


if __name__ == "__main__":
    try:
        asyncio.run(text_interaction())
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
