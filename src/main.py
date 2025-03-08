"""
CNC Machine Warmup Generator - Main Script
Author: John Germing
Date: 2025-03-08
Description: This script generates a Heidenhain-compatible CNC warmup G-code
             program based on user-defined machine parameters.
"""

from config import MACHINES, DEFAULT_SETTINGS

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

if __name__ == "__main__":
    main()