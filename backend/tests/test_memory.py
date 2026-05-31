import pytest
from memory.engine import MemoryEngine

@pytest.mark.asyncio
async def test_memory_engine_init():
    engine = MemoryEngine()
    assert engine is not None

@pytest.mark.asyncio
async def test_add_episode():
    engine = MemoryEngine()
    await engine.add_episode("TEST_EVENT", "This is a test", {})
    # Assert side effects once DB is implemented
