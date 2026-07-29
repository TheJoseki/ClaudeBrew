#!/usr/bin/env python3
"""
ClaudeKit WBS Estimate Calculator — Sprint 3 script
Deterministic MD/MM calculation. Code is more reliable than language instructions for math.

Usage:
  python calc_estimate.py --points 3 5 8 2 3 --team 2
  python calc_estimate.py --points 3 5 8 2 3 --team 2 --velocity 0.5
  python calc_estimate.py --points 3 5 8 2 3 --team 1 --velocity 0.5 --working-days 22

Invoke from SKILL.md Step 3 instead of asking Claude to calculate manually.
"""

import argparse
import sys


def calculate_buffer(total_points: int) -> tuple[float, str]:
    """Return (buffer_ratio, tier_name) based on complexity tier."""
    if total_points <= 20:
        return 0.10, "Simple (≤20 pts) → +10%"
    elif total_points <= 60:
        return 0.20, "Medium (21–60 pts) → +20%"
    else:
        return 0.30, "Large (61+ pts) → +30%"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ClaudeKit WBS estimate calculator — converts story points to MD/MM"
    )
    parser.add_argument(
        "--points", nargs="+", type=int, required=True,
        help="Story points for each task (space-separated). Example: --points 3 5 8 2 3"
    )
    parser.add_argument(
        "--team", type=int, default=1,
        help="Number of developers working in parallel (default: 1)"
    )
    parser.add_argument(
        "--velocity", type=float, default=0.5,
        help="Developer-days per story point (default: 0.5)"
    )
    parser.add_argument(
        "--working-days", type=int, default=20,
        help="Working days per month used to calculate MM (default: 20)"
    )

    args = parser.parse_args()

    total_points = sum(args.points)
    raw_md = total_points * args.velocity
    buffer_ratio, buffer_label = calculate_buffer(total_points)
    adjusted_md = raw_md * (1 + buffer_ratio)
    adjusted_mm = adjusted_md / args.working_days
    calendar_days = adjusted_md / args.team
    calendar_weeks = calendar_days / 5

    print("=" * 55)
    print("  ClaudeKit WBS Estimate Result")
    print("=" * 55)
    print(f"  Tasks analyzed       : {len(args.points)}")
    print(f"  Story points (total) : {total_points}")
    print(f"  Velocity used        : {args.velocity} dev-days / pt")
    print(f"  Raw effort           : {raw_md:.1f} man-days")
    print(f"  Buffer tier          : {buffer_label}")
    print(f"  Buffer amount        : +{raw_md * buffer_ratio:.1f} days")
    print(f"  Adjusted effort (MD) : {adjusted_md:.1f} man-days")
    print(f"  Adjusted effort (MM) : {adjusted_mm:.2f} man-months")
    print(f"  Team size            : {args.team} developer(s)")
    print(f"  Calendar duration    : {calendar_days:.1f} days ≈ {calendar_weeks:.1f} weeks")
    print("=" * 55)

    if total_points > 60:
        print("  ⚠  Large feature — consider splitting into sub-features")
        print("     for more accurate estimation and better sprint planning.")


if __name__ == "__main__":
    main()
