"""System resource monitor — CPU, RAM, and (optionally) GPU."""

from __future__ import annotations

import asyncio
import subprocess
import sys

import psutil

from llm_runtime.schemas import ResourceUsage
from shared.logging_config import get_logger

logger = get_logger(__name__)


async def get_resource_usage() -> ResourceUsage:
    """Collect a snapshot of system resources, including GPU when available."""
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()

    usage = ResourceUsage(
        cpu_percent=cpu,
        ram_total_gb=round(mem.total / (1024**3), 2),
        ram_used_gb=round(mem.used / (1024**3), 2),
        ram_available_gb=round(mem.available / (1024**3), 2),
    )

    # Attempt to read GPU via nvidia-smi
    gpu = await _query_nvidia_smi()
    if gpu:
        usage.gpu_name = gpu.get("name")
        usage.gpu_vram_total_mb = gpu.get("memory_total")
        usage.gpu_vram_used_mb = gpu.get("memory_used")
        usage.gpu_vram_free_mb = gpu.get("memory_free")
        usage.gpu_utilization_percent = gpu.get("utilization")

    return usage


async def _query_nvidia_smi() -> dict | None:
    """Parse nvidia-smi output. Returns None if nvidia-smi is absent."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu",
            "--format=csv,noheader,nounits",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        line = stdout.decode().strip().split("\n")[0]
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 5:
            return {
                "name": parts[0],
                "memory_total": int(parts[1]),
                "memory_used": int(parts[2]),
                "memory_free": int(parts[3]),
                "utilization": float(parts[4]),
            }
    except (FileNotFoundError, asyncio.TimeoutError, Exception):
        pass
    return None
