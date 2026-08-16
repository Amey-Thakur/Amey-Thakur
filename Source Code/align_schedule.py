# ==============================================================================
# File: align_schedule.py
# Author: Amey Thakur
# Profile: https://github.com/Amey-Thakur
# Repository: https://github.com/Amey-Thakur/Amey-Thakur
# Release Date: August 16, 2026
# Modified: August 16, 2026
# License: MIT License
# ==============================================================================
#
# DESCRIPTION:
# Keeps the workflow firing at local midnight and local noon, by recording what
# time each run actually happened and correcting the cron when the pattern
# shows it has drifted.
#
# HOW IT WORKS:
# GitHub schedules in UTC and offers no way to express a local time, so a cron
# written for one offset is wrong for half the year and wrong permanently after
# a move. Rather than trusting a single reading, every run appends what it
# observed to a small ledger: the UTC moment it fired, the offset in force, and
# the resulting local hour.
#
# The cron is only rewritten once several consecutive runs agree on a new
# offset. A single bad reading, from a failed request or a page that briefly
# omitted the attribute, therefore cannot move the schedule on its own. The
# ledger is committed alongside the cards, so the reasoning behind any change
# stays visible in the history.
#
# TECH STACK:
# - Python standard library only, so the workflow installs nothing to run it
#
# ==============================================================================

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from local_time import local_now, offset_hours

# Each workflow keeps its own schedule, so each one names its own file when it
# calls this. Aligning a fixed path would let one workflow rewrite another's
# cron, which is exactly the coupling that keeping them separate avoids.
WORKFLOW = Path(os.environ.get("WORKFLOW_FILE", ".github/workflows/languages.yml"))

# One ledger per workflow, named after the workflow that writes it. A shared
# file meant two jobs creating the same path in the same second, which is an
# add/add conflict that no rebase can resolve and which failed a run.
LEDGER = Path("docs") / f"schedule_state_{WORKFLOW.stem}.json"

# The local hours the cards are due.
DUE_LOCAL_HOURS = (0, 12)

# How many consecutive runs must agree before the schedule is moved. Two runs a
# day means a genuine change is acted on within about a day, while a one-off
# misread is discarded.
AGREEMENT_REQUIRED = 3

# How much history to keep. Enough to show a daylight saving transition in
# context without the file growing without bound.
LEDGER_LIMIT = 40

# Only the hour field is ever rewritten. Holding the rest of the expression
# fixed means a malformed offset cannot produce a schedule that fires
# constantly.
CRON_LINE = re.compile(r"^(\s*- cron: ')(\d+) [\d,]+( \* \* \*')$", re.M)


def utc_hours_for(offset):
    """The UTC hours matching the due local hours at a given offset.

    Offsets are not always whole hours. At +5.5 local midnight falls at 18:30
    UTC and the job fires at 18:00, half an hour early, which is as close as a
    single cron entry can get.
    """
    return sorted({int((hour - offset) % 24) for hour in DUE_LOCAL_HOURS})


def cron_for(offset, minute=0):
    """The cron expression for a given offset, keeping the stagger minute."""
    return f"{minute} " + ",".join(str(h) for h in utc_hours_for(offset)) + " * * *"


def read_ledger():
    if not LEDGER.exists():
        return []
    try:
        return json.loads(LEDGER.read_text(encoding="utf-8")).get("runs", [])
    except Exception:
        # A corrupt ledger is recoverable: the schedule stays as it is and the
        # record starts again, rather than the run failing.
        return []


def write_ledger(runs, offset):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(
        json.dumps(
            {
                "note": "Written by align_schedule.py. One entry per workflow run.",
                "current_offset_hours": offset,
                "current_offset_note": "cron minute differs per workflow; see each file",
                "runs": runs[-LEDGER_LIMIT:],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def settled_offset(runs):
    """The offset if the most recent runs agree on it, otherwise None."""
    recent = [r["offset"] for r in runs[-AGREEMENT_REQUIRED:]]
    if len(recent) < AGREEMENT_REQUIRED:
        return None
    return recent[0] if len(set(recent)) == 1 else None


def main():
    offset = offset_hours()
    now_local = local_now()

    runs = read_ledger()
    runs.append(
        {
            "fired_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "local": now_local.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "local_hour": now_local.hour,
            "offset": offset,
        }
    )
    write_ledger(runs, offset)

    print(f"Fired at {now_local:%Y-%m-%d %H:%M} local, offset {offset:+.2f}.")

    if not WORKFLOW.exists():
        print("No workflow file to align.")
        return 0

    text = WORKFLOW.read_text(encoding="utf-8")
    match = CRON_LINE.search(text)
    if not match:
        print("::warning::No cron line found to check.")
        return 0

    current = re.search(r"'([^']+)'", match.group(0)).group(1)
    minute = int(current.split()[0])
    wanted = cron_for(offset, minute)

    if current == wanted:
        print(f"Schedule is correct: '{current}'.")
        return 0

    agreed = settled_offset(runs)
    if agreed is None or cron_for(agreed, minute) != wanted:
        seen = [r["offset"] for r in runs[-AGREEMENT_REQUIRED:]]
        print(
            f"Schedule would move to '{wanted}', holding until "
            f"{AGREEMENT_REQUIRED} runs agree. Recent offsets: {seen}."
        )
        return 0

    WORKFLOW.write_text(
        CRON_LINE.sub(lambda m: f"{m.group(1)}{wanted[:-6]}{m.group(3)}", text, count=1),
        encoding="utf-8",
        newline="\n",
    )
    print(f"Offset settled at {agreed:+.2f} over {AGREEMENT_REQUIRED} runs.")
    print(f"Schedule rewritten from '{current}' to '{wanted}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
