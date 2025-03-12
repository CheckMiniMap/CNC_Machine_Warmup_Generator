"""
CNC Machine Warmup Generator - Main Script
Author: John Germing
Date: 2025-03-08
Description: This script will prompt for user-defined machine parameters 
             to generate a Heidenhain TNC640 or Fanuc 31i controller 
             compatible CNC warmup G-code program.
"""

import os
from config import MACHINES, DEFAULT_SETTINGS
from generator import generate_gcode_heidenhain, generate_gcode_fanuc

def main():
    """ Main function to execute the warmup G-code generator. """
    print("Heidenhain CNC Warmup Program Generator\n")

    # Select machine configuration
    print("Available Machine Configurations:")
    # Iterate through machine types in dictionary config and print them out.
    for key, machine in MACHINES.items():
        print(f"{key}: X Travel: {machine['X']} mm, Y Travel: {machine['Y']} mm")

    # Prompt user for machine selection
    machine_choice = input("Select a machine number (1-3): ").strip()
    if machine_choice not in MACHINES:
        print("Invalid selection. Exiting.")
        return
    else:
        print(f"You selected Machine {machine_choice}.\n\t- X Travel Limit: {MACHINES[machine_choice]['X']} mm\n\t- Y Travel Limit: {MACHINES[machine_choice]['Y']} mm")

    # Define warmup parameters
    print("Note: DEFAULT VALUE = [#]")
    # Get user inputs while allowing for falsy values with defaults.
    start_rpm = int(input(f"Enter start spindle RPM [{DEFAULT_SETTINGS['start_rpm']}]: ") or DEFAULT_SETTINGS["start_rpm"])
    finish_rpm = int(input(f"Enter finish spindle RPM [{DEFAULT_SETTINGS['finish_rpm']}]: ") or DEFAULT_SETTINGS["finish_rpm"])
    start_feed = int(input(f"Enter start feedrate [{DEFAULT_SETTINGS['start_feedrate']}]: ") or DEFAULT_SETTINGS["start_feedrate"])
    finish_feed = int(input(f"Enter finish feedrate [{DEFAULT_SETTINGS['finish_feedrate']}]: ") or DEFAULT_SETTINGS["finish_feedrate"])
    coolant = input("Enable coolant? (yes/no) [yes]: ").strip().lower() != "no"
    tool_call_num = int(input(f"Enter tool call number [{DEFAULT_SETTINGS['tool_call_num']}]: ") or DEFAULT_SETTINGS["tool_call_num"])
    increment_steps = int(input(f"Enter # of incremental steps (higher = more gradual speed ramp-up) [{DEFAULT_SETTINGS['increment_steps']}]: ") or DEFAULT_SETTINGS["increment_steps"])

    # Generate G-code based on CNC type and machine parameters.
    machine_params = MACHINES[machine_choice]
    gcode = ""
    # Prompt for CNC controller type selection with falsy default value.
    cnc_type = int(input("Select CNC type # (1 = Heidenhain, 2 = Fanuc) [1]: ") or 1)
    # Call specific G-code generator function based on type of CNC controller.
    if cnc_type == 1:
        gcode = generate_gcode_heidenhain(machine_params, start_rpm, finish_rpm, start_feed, finish_feed, coolant, tool_call_num, increment_steps)
    elif cnc_type == 2:
        gcode = generate_gcode_fanuc(machine_params, start_rpm, finish_rpm, start_feed, finish_feed, coolant, tool_call_num, increment_steps)
    else:
        print("Invalid CNC type selected. Exiting.")
        return

    # Save to custom file name based on cnc_type and machine choice.
    # Utilizing ternary operators to determine controller type and file name.
    controller_type = "tnc640" if cnc_type == 1 else "r31i"
    file_name = input(f"Enter output file name (default: warmup_{controller_type}_{machine_choice}): ").strip()
    # If no file name is provided, use the default naming convention.
    # Also, strip the file extension if the user inputted one. 
    file_name = f"warmup_{controller_type}_{machine_choice}" if not file_name else (file_name.removesuffix(".H") if file_name.endswith(".H") else file_name.removesuffix(".NC") if file_name.endswith(".NC") else file_name)

    # Output generated G-Code in "/outputs" directory.
    output_file = f"output/{file_name}.H" if cnc_type == 1 else f"output/{file_name}.NC"
    # Create directory if it does not exist.
    os.makedirs("output", exist_ok=True)

    # Write all generated G-Code into file.
    with open(output_file, "w") as file:
        file.write(gcode)

    print(f"\nG-code successfully generated and saved to: {output_file}")


if __name__ == "__main__":
    main()