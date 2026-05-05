import asyncio
import time

# These are counters stored in memory
_total_signals    = 0       # total signals received since server started
_window_signals   = 0       # signals received in the last 5 seconds
_window_start     = time.time()  # when the current 5-second window started
_peak_rate        = 0.0     # highest signals/sec ever recorded

def record_signal():
    """Call this every time a signal is received."""
    global _total_signals, _window_signals
    _total_signals  += 1
    _window_signals += 1

def get_metrics() -> dict:
    """Return current metrics — used by /health endpoint."""
    elapsed = time.time() - _window_start
    current_rate = round(_window_signals / elapsed, 2) if elapsed > 0 else 0
    return {
        "total_signals_received": _total_signals,
        "current_rate_per_sec":   current_rate,
        "peak_rate_per_sec":      _peak_rate,
        "uptime_seconds":         round(elapsed, 1),
    }

async def metrics_printer():
    """
    Runs forever in the background.
    Every 5 seconds, prints throughput to the console.
    """
    global _window_signals, _window_start, _peak_rate

    print("Metrics printer started — reporting every 5 seconds")
    while True:
        await asyncio.sleep(5)

        now     = time.time()
        elapsed = now - _window_start

        # Calculate signals per second in this window
        rate = round(_window_signals / elapsed, 2) if elapsed > 0 else 0

        # Track peak rate
        if rate > _peak_rate:
            _peak_rate = rate

        # Print to console
        print(
            f"[METRICS] "
            f"Signals/sec: {rate} | "
            f"Window total: {_window_signals} | "
            f"All-time total: {_total_signals} | "
            f"Peak: {_peak_rate}/sec"
        )

        # Reset window counters for next 5 seconds
        _window_signals = 0
        _window_start   = now