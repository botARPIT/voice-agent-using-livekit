"""
Simple test client to connect to the Real Estate Voice Agent.
This simulates a user connecting to the agent room.
"""

import asyncio
import os

from dotenv import load_dotenv
from livekit import api, rtc

load_dotenv()


async def connect_to_agent():
    """Connect to the voice agent room."""
    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not all([url, api_key, api_secret]):
        print("Error: Please set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET in .env")
        return

    # Create access token
    token = api.AccessToken(api_key, api_secret)
    token.with_identity("test-user")
    token.with_grants(api.VideoGrants(
        room_join=True,
        room="test-room-001",
        can_publish=True,
        can_subscribe=True,
    ))

    token_str = token.to_jwt()
    print(f"Generated token: {token_str[:50]}...")

    # Connect to room
    room = rtc.Room()

    @room.on("connected")
    def on_connected():
        print(f"✓ Connected to room: {room.name}")
        print("Waiting for agent to join...")

    @room.on("disconnected")
    def on_disconnected():
        print("Disconnected from room")

    @room.on("track_subscribed")
    def on_track_subscribed(track, publication, participant):
        print(f"✓ Subscribed to {track.kind} track from {participant.identity}")
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            print("Agent audio connected - you can now speak!")

    @room.on("participant_connected")
    def on_participant_connected(participant):
        print(f"✓ Participant joined: {participant.identity}")

    print(f"Connecting to {url}...")
    await room.connect(url, token_str)

    # Keep connection alive
    try:
        while room.connection_state != rtc.ConnectionState.CONN_DISCONNECTED:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        await room.disconnect()


if __name__ == "__main__":
    asyncio.run(connect_to_agent())
