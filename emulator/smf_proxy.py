# Calibration constants — adjust via calibrate() after benchmarking
# against a known z/Architecture workload on the host machine.
MIPS_RATIO: float = 1_000_000.0  # instructions per MIPS at reference clock
COST_PER_MIPS_PER_MONTH: float = 300.0  # conservative enterprise $/MIPS/month


def instructions_to_mips(instruction_count: int, elapsed_seconds: float) -> float:
    if elapsed_seconds <= 0:
        return 0.0
    return (instruction_count / elapsed_seconds) / MIPS_RATIO


def mips_reduction_pct(baseline_mips: float, optimized_mips: float) -> float:
    if baseline_mips <= 0:
        return 0.0
    return (baseline_mips - optimized_mips) / baseline_mips * 100.0


def mips_to_monthly_saving(mips_reduction: float) -> float:
    return mips_reduction * COST_PER_MIPS_PER_MONTH


def calibrate(reference_instructions: int, reference_mips: float, elapsed: float) -> None:
    """Refit MIPS_RATIO from a known benchmark. Call once after HERCULES setup."""
    global MIPS_RATIO
    if reference_mips > 0 and elapsed > 0:
        MIPS_RATIO = (reference_instructions / elapsed) / reference_mips
