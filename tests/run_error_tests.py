#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from exodus_calendar.utils import YEAR_CYCLE, MARS_YEAR_LENGTH, EARTH_YEAR_LENGTH, DAY_LENGTH
from exodus_calendar.utils import MARS_SECOND_LENGTH, SOL_LENGTH

# Calendar parameters
fixed_year = (668*10+669*11+670)/22.0  # Fixed calendar year length
true_year_epoch = 668.5907  # True year at epoch (t=0)
rate_change = 0.00079  # Rate of change per 1000 years


def true_year_length(t):
    """True equinox year length as function of time (in Martian years)"""
    return true_year_epoch + rate_change * t / 1000

def accumulated_error(t):
    constant_diff = fixed_year - true_year_epoch
    error = constant_diff * t  - rate_change * t**2 / (2 * 1000)
    return error

def main():
    # Time range: 0 to 2000 Martian years to show -1 sol point clearly
    t = np.linspace(0, 2000, 200)

    # Calculate true year lengths over time
    true_years = true_year_length(t)

    # Calculate accumulated errors
    errors = accumulated_error(t)

    # Create plots
    fig, ax3 = plt.subplots(1, 1, figsize=(8, 6))

    # Plot A: Accumulated error with key milestones marked
    ax3.plot(t, errors, 'r-', linewidth=2, label='Accumulated error')
    ax3.set_xlabel('Time (Martian years)')
    ax3.set_ylabel('Accumulated error (sols)')
    ax3.set_title('Accumulated Calendar Error Over Time')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0, color='k', linestyle='-', alpha=0.5)

    # Mark key points
    # Maximum error point
    max_error_time = 1000 * (fixed_year - true_year_epoch) / rate_change
    max_error_value = accumulated_error(max_error_time)
    label_str_pos = f'Max positive error: +{max_error_value:.2f} sols at T+{max_error_time:.0f} years'
    ax3.plot(max_error_time, max_error_value, 'go', markersize=8, label= label_str_pos)

    # -1 sol error point
    # Solve quadratic: 0.000000395*t² - 0.0002090909*t - 1 = 0
    a = rate_change/(2*1000)
    b = true_year_epoch-fixed_year
    c = -1
    d = b**2 - 4*a*c
    t_minus_1 = (-b + np.sqrt(d)) / (2*a)
    if t_minus_1 <= 2500:  # Only plot if within range
        label_str_neg = f'Error of -1.0 sol accumulates by T+{t_minus_1:.0f} years'
        ax3.plot(t_minus_1, -1, 'ro', markersize=8, label=label_str_neg)
    ax3.axhline(y=-1, color='r', linestyle='--', alpha=0.5)


    ax3.legend()
    ax3.set_ylim(-2, 1)

    plt.tight_layout()
    plt.show()

    # Print some key values
    print("Martian Calendar Error Analysis")
    print("=" * 40)
    print(f"Fixed calendar year: {fixed_year:.10f} sols")
    print(f"True year at epoch: {true_year_epoch:.7f} sols")
    print(f"Initial difference: {fixed_year - true_year_epoch:.10f} sols")
    print(f"Rate of change: {rate_change:.5f} sols per 1000 years")
    print()

    # Calculate when calendar catches up to true year
    # Solve: fixed_year = true_year_epoch + rate_change * t / 1000
    # t = 1000 * (fixed_year - true_year_epoch) / rate_change
    catch_up_time = 1000 * (fixed_year - true_year_epoch) / rate_change
    # Calculate when calendar catches up to true year
    # Solve: fixed_year = true_year_epoch + rate_change * t / 1000
    # t = 1000 * (fixed_year - true_year_epoch) / rate_change
    catch_up_time = 1000 * (fixed_year - true_year_epoch) / rate_change
    print(f"Calendar catches up to true year at: {catch_up_time:.1f} Martian years")

    # Let me double-check this calculation step by step
    initial_diff = fixed_year - true_year_epoch
    print(f"\nStep-by-step verification:")
    print(f"Fixed calendar year: {fixed_year:.10f} sols")
    print(f"True year at epoch: {true_year_epoch:.7f} sols") 
    print(f"Initial difference: {initial_diff:.10f} sols")
    print(f"Rate of change: {rate_change:.5f} sols per 1000 years")
    print(f"Catch-up time = 1000 × {initial_diff:.10f} / {rate_change:.5f} = {catch_up_time:.1f} years")

    # Maximum accumulated error occurs at catch-up point
    max_error = accumulated_error(catch_up_time)
    print(f"Maximum accumulated error: {max_error:.6f} sols at {catch_up_time:.1f} years")

    # Error at various time points
    time_points = [265, 529, 1000, 1350, 1878]
    print("\nAccumulated errors at key time points:")
    for tp in time_points:
        error = accumulated_error(tp)
        print(f"  {tp:5d} years: {error:+8.3f} sols ({error*24:+8.1f} hours)")

    # Days offset (assuming 24.62-hour Martian day)
    martian_day_hours = 24.62
    print(f"\nNote: 1 sol = {martian_day_hours} Earth hours")

    # Analytical formula
    print("\nAccumulated Error Function:")
    print("E(t) = 0.0002090909 × t - 0.000000395 × t²")
    print("where t is time in Martian years, E(t) is error in sols")

main()