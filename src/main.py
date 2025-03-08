"""
CNC Machine Warmup Generator - Main Script
Author: John Germing
Date: 2025-03-08
Description: This script generates a Heidenhain-compatible CNC warmup G-code
             program based on user-defined machine parameters.
"""

import os
from config import MACHINES, DEFAULT_SETTINGS
from generator import generate_gcode

def main():
    """ Main function to execute the warmup G-code generator. """
    print("Heidenhain CNC Warmup Program Generator\n")

    # Select machine configuration
    print("Available Machine Configurations:")
    for key, machine in MACHINES.items():
        print(f"{key}: X Travel: {machine['X']} mm, Y Travel: {machine['Y']} mm")

    machine_choice = input("Select a machine number (1-3): ").strip()
    if machine_choice not in MACHINES:
        print("Invalid selection. Exiting.")
        return
    else:
        print(f"You selected Machine {machine_choice}.\n\t- X Travel Limit: {MACHINES[machine_choice]['X']} mm\n\t- Y Travel Limit: {MACHINES[machine_choice]['Y']} mm")

    # Define warmup parameters
    start_rpm = int(input(f"Enter start spindle RPM [{DEFAULT_SETTINGS['start_rpm']}]: ") or DEFAULT_SETTINGS["start_rpm"])
    finish_rpm = int(input(f"Enter finish spindle RPM [{DEFAULT_SETTINGS['finish_rpm']}]: ") or DEFAULT_SETTINGS["finish_rpm"])
    start_feed = int(input(f"Enter start feedrate [{DEFAULT_SETTINGS['start_feedrate']}]: ") or DEFAULT_SETTINGS["start_feedrate"])
    finish_feed = int(input(f"Enter finish feedrate [{DEFAULT_SETTINGS['finish_feedrate']}]: ") or DEFAULT_SETTINGS["finish_feedrate"])
    coolant = input("Enable coolant? (yes/no) [yes]: ").strip().lower() != "no"

    # Generate G-code
    machine_params = MACHINES[machine_choice]
    gcode = generate_gcode(machine_params, start_rpm, finish_rpm, start_feed, finish_feed, coolant)

    # Save to file
    file_name = input(f"Enter output file name (default: warmup_machine_{machine_choice}): ").strip()
    file_name = f"warmup_machine_{machine_choice}" if not file_name else file_name.removesuffix(".H")

    output_file = f"output/{file_name}.H"
    os.makedirs("output", exist_ok=True)

    with open(output_file, "w") as file:
        file.write(gcode)

    print(f"\nG-code successfully generated and saved to: {output_file}")


if __name__ == "__main__":
    main()