"""Pydantic v2 models for SMF record types used by Z-Optima RL."""

import datetime

from pydantic import BaseModel, Field


class SMFHeader(BaseModel):
    """Common fields present on every SMF record."""
    rdw_length: int
    smf_type: int
    flags: int
    date: datetime.date
    time: datetime.time


class SMFType30(BaseModel):
    """SMF Type 30 subtype 4 — step termination record.

    Fields map directly to SMFStateVector in env/v2/state.py.
    """
    # Job identification
    job_name: str
    step_name: str
    program_name: str
    # Timing & I/O
    cpu_time_us: int = 0
    elapsed_time_us: int = 0
    excp_count: int = 0
    mips_estimate: float | None = None
    # Outcome
    return_code: int = 0
    # When the record was written
    date: datetime.date = Field(default_factory=datetime.date.today)
    time: datetime.time = Field(default_factory=lambda: datetime.datetime.now().time())


class SMFType72(BaseModel):
    """SMF Type 72 — RMF workload activity summary."""
    date: datetime.date = Field(default_factory=datetime.date.today)
    time: datetime.time = Field(default_factory=lambda: datetime.datetime.now().time())
    service_units: int = 0
    cpu_delay_ms: int = 0
    io_delay_ms: int = 0
    mso_delay_ms: int = 0


class SMFType74(BaseModel):
    """SMF Type 74 — RMF device activity (channel/DASD)."""
    date: datetime.date = Field(default_factory=datetime.date.today)
    time: datetime.time = Field(default_factory=lambda: datetime.datetime.now().time())
    device_number: int = 0
    io_rate: float = 0.0
    utilization_pct: float = 0.0
