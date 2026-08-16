# ==============================================================================
# File: local_time.py
# Author: Amey Thakur
# Profile: https://github.com/Amey-Thakur
# Repository: https://github.com/Amey-Thakur/Amey-Thakur
# License: MIT License
# ==============================================================================
#
# DESCRIPTION:
# Resolves the author's current local time so the profile cards can be
# regenerated at local midnight and local noon rather than at a fixed UTC hour.
#
# HOW IT WORKS:
# GitHub publishes the profile's UTC offset on the profile page itself, in a
# `data-hours-ahead-of-utc` attribute. That is the only source which follows
# both daylight saving and an actual change of country without anything in this
# repository being edited, which is why it is preferred over a hard-coded zone.
#
# TECH STACK:
# - Python standard library only, so the workflow needs no dependencies
#
# ==============================================================================

import re
import subprocess
import urllib.request
from datetime import datetime, timedelta, timezone

PROFILE_URL = "https://github.com/Amey-Thakur"

# GitHub renders the offset as a float, because not every zone is a whole
# number of hours away from UTC. India is +5.5, Nepal is +5.75.
_PROFILE_OFFSET = re.compile(r'data-hours-ahead-of-utc="(-?\d+(?:\.\d+)?)"')

# `git log --date=iso-strict` writes UTC as a bare "Z" and everything else as
# "+HH:MM" or "-HH:MM".
_GIT_OFFSET = re.compile(r"([+-])(\d{2}):(\d{2})$")

_REQUEST_HEADERS = {"User-Agent": "Amey-Thakur-profile-cards"}


def _offset_from_profile(timeout=15):
    """Read the UTC offset straight from the GitHub profile page.

    Returns the offset in hours, or None when the profile does not publish one.
    A profile only carries the attribute while "display current local time" is
    switched on in settings, so absence is an ordinary outcome, not an error.
    """
    try:
        request = urllib.request.Request(PROFILE_URL, headers=_REQUEST_HEADERS)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            page = response.read().decode("utf-8", "replace")
    except Exception:
        return None

    match = _PROFILE_OFFSET.search(page)
    return float(match.group(1)) if match else None


def _offset_from_git():
    """Fall back to the offset carried by the most recent human commit.

    Every commit records the timezone it was authored in, so the history knows
    where its author was. The catch is that the workflow's own commits are made
    on a runner and are stamped UTC, and they are the most recent commits in
    this repository almost all of the time. Reading only the newest commit
    therefore reports UTC no matter where the author actually is, which is the
    bug this function exists to avoid: it walks back until it finds a commit
    that was not written in UTC.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-80", "--format=%ad", "--date=iso-strict"],
            capture_output=True, text=True, check=True,
        )
    except Exception:
        return None

    for line in result.stdout.splitlines():
        match = _GIT_OFFSET.search(line.strip())
        if not match:
            continue                      # a bare "Z", so a runner commit
        sign, hours, minutes = match.groups()
        offset = int(hours) + int(minutes) / 60
        return -offset if sign == "-" else offset
    return None


def offset_hours():
    """The author's current offset from UTC, in hours.

    Tries the profile first because it is the only source that stays correct on
    its own, then the commit history, then gives up and reports UTC so that a
    network failure degrades to something predictable rather than crashing.
    """
    for source in (_offset_from_profile, _offset_from_git):
        offset = source()
        if offset is not None:
            return offset
    return 0.0


def local_zone():
    """The author's current timezone, as a fixed offset from UTC."""
    return timezone(timedelta(hours=offset_hours()))


def local_now():
    """The current moment, in the author's local time."""
    return datetime.now(local_zone())


def is_scheduled_hour(hours=(0, 12)):
    """Is it one of the hours the cards are meant to be rebuilt?

    The workflow is scheduled hourly and asks this question each time, rather
    than being pinned to a UTC hour. A fixed cron drifts by an hour twice a year
    at the daylight saving boundary, and breaks entirely on a change of country.
    """
    return local_now().hour in hours


if __name__ == "__main__":
    # Running the module directly prints what the workflow gate needs, which
    # also makes it easy to check by hand.
    now = local_now()
    print(f"offset  : {offset_hours():+.2f} hours from UTC")
    print(f"local   : {now:%Y-%m-%d %H:%M:%S %z}")
    print(f"utc     : {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S}")
    print(f"due now : {is_scheduled_hour()}")
