"""
Natural Language System Interface - Debugged Version
Author: DeepSeek-R1 (debugged)
Ensures valid command generation and execution
"""

import os
import re
import subprocess
from ollama import Client

class NaturalSystemInterface:
    def __init__(self):
        self.client = Client(host='http://localhost:11434')
        self._init_safety_parameters()
        self.command_history = []

    def _init_safety_parameters(self):
        self.allowed_paths = [
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            "/tmp"
        ]
        self.unsafe_patterns = [
            r"\brm\s+-rf\b", r"\bsudo\b", r"chmod\s+[0-7]{3,4}",
            r">\s+/", r"\bmkfs\b", r"\bdd\s+if=", r"\|", r";",
            r"\bpoweroff\b", r"\breboot\b", r"\bpkill\b"
        ]

    def generate_command(self, prompt: str) -> str:
        """Improved command generation with strict formatting"""
        try:
            response = self.client.generate(
                model='llama3.2',
                prompt=f"""STRICTLY CONVERT TO LINUX COMMAND ONLY. NO EXPLANATION. NO MARKDOWN.
                Example1: 'list files' → 'ls -l'
                Example2: 'show documents' → 'ls ~/Documents'
                Input: {prompt}
                Command:"""
            )
            # Clean response using multiple methods
            command = response['response'].strip()
            command = re.sub(r'^["\'`]|["\'`]$', '', command)  # Remove quotes/backticks
            command = re.split(r'[#\n]', command)[0].strip()  # Remove comments/newlines
            return command
        except Exception as e:
            print(f"Command generation error: {str(e)}")
            return ""

    def is_command_safe(self, command: str) -> bool:
        """Enhanced safety check with path validation"""
        if not command:
            return False
            
        # Block unsafe patterns
        if any(re.search(pattern, command) for pattern in self.unsafe_patterns):
            return False

        # Validate file paths
        try:
            expanded_command = os.path.expanduser(command)
            matches = re.finditer(r'(?<!\\)[\'"]?((?:/\S+)+|~\S*)[\'"]?', expanded_command)
            for match in matches:
                path = os.path.abspath(os.path.expandvars(match.group(1)))
                if not any(path.startswith(allowed) for allowed in self.allowed_paths):
                    return False
        except:
            return False

        return True

    def execute_command(self, command: str) -> str:
        """Robust command execution with error handling"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                executable="/bin/bash",
                capture_output=True,
                text=True,
                timeout=15
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            return "Error: Command timed out (15s limit)"
        except Exception as e:
            return f"Execution error: {str(e)}"

    def run_interface(self):
        """Improved interactive interface"""
        print("Natural Command Interface (type 'history' or 'exit')")
        while True:
            try:
                user_input = input("\n> ").strip().lower()
                
                if user_input == 'history':
                    print("\nCommand History:")
                    for idx, cmd in enumerate(self.command_history, 1):
                        print(f"{idx}. {cmd}")
                    continue
                
                if user_input in ('exit', 'quit'):
                    break

                # Generate and validate command
                command = self.generate_command(user_input)
                if not command:
                    print("Error: Could not generate valid command")
                    continue
                    
                if not self.is_command_safe(command):
                    print("Blocked: Command violates security rules")
                    continue

                # Confirm destructive operations
                if any(kw in command for kw in ["rm", "mv", "cp"]) and \
                   input(f"Confirm '{command}'? (y/n): ").lower() != 'y':
                    continue

                # Execute and store
                result = self.execute_command(command)
                print(f"\n{result}")
                self.command_history.append(command)

            except KeyboardInterrupt:
                print("\nExiting safely...")
                break
            except Exception as e:
                print(f"System error: {str(e)}")
                continue

if __name__ == "__main__":
    NaturalSystemInterface().run_interface()
