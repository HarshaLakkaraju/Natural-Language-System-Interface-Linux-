import os  # Import the os module for interacting with the operating system
import re  # Import the re module for regular expressions
import subprocess  # Import the subprocess module for spawning new processes
from ollama import Client  # Import the Client class from the ollama module

class NaturalSystemInterface:
    def __init__(self):
        # Initialize the Client to connect to a local service
        self.client = Client(host='http://localhost:11434')
        # Initialize safety parameters
        self._init_safety_parameters()
        # Initialize an empty list to keep track of executed commands
        self.command_history = []

    def _init_safety_parameters(self):
        # Define allowed file paths
        self.allowed_paths = [
            os.path.expanduser("~/Documents"),  # User's Documents directory
            os.path.expanduser("~/Downloads"),  # User's Downloads directory
            "/tmp"  # Temporary directory
        ]
        # Define unsafe command patterns to block
        self.unsafe_patterns = [
            r"\brm\s+-rf\b",  # Pattern for 'rm -rf'
            r"\bsudo\b",  # Pattern for 'sudo'
            r"chmod\s+[0-7]{3,4}",  # Pattern for 'chmod' with permissions
            r">\s+/",  # Pattern for redirection to root
            r"\bmkfs\b",  # Pattern for 'mkfs'
            r"\bdd\s+if=",  # Pattern for 'dd if='
            r"\|",  # Pattern for pipe '|'
            r";",  # Pattern for command separator ';'
            r"\bpoweroff\b",  # Pattern for 'poweroff'
            r"\breboot\b",  # Pattern for 'reboot'
            r"\bpkill\b"  # Pattern for 'pkill'
        ]

    def generate_command(self, prompt: str) -> str:
        """Improved command generation with strict formatting"""
        try:
            # Generate a Linux command from a natural language prompt using the Client
            response = self.client.generate(
                model='llama3.2',
                prompt=f"""STRICTLY CONVERT TO LINUX COMMAND ONLY. NO EXPLANATION. NO MARKDOWN.
                Example1: 'list files' → 'ls -l'
                Example2: 'show documents' → 'ls ~/Documents'
                Input: {prompt}
                Command:"""
            )
            # Clean the response by removing quotes, backticks, comments, and newlines
            command = response['response'].strip()
            command = re.sub(r'^["\'`]|["\'`]$', '', command)
            command = re.split(r'[#\n]', command)[0].strip()
            return command
        except Exception as e:
            # Print an error message if command generation fails
            print(f"Command generation error: {str(e)}")
            return ""

    def is_command_safe(self, command: str) -> bool:
        """Enhanced safety check with path validation"""
        if not command:
            # Return False if the command is empty
            return False

        # Block unsafe patterns
        if any(re.search(pattern, command) for pattern in self.unsafe_patterns):
            return False

        try:
            # Expand user paths in the command
            expanded_command = os.path.expanduser(command)
            # Find all file paths in the command
            matches = re.finditer(r'(?<!\\)[\'"]?((?:/\S+)+|~\S*)[\'"]?', expanded_command)
            for match in matches:
                # Validate each file path
                path = os.path.abspath(os.path.expandvars(match.group(1)))
                if not any(path.startswith(allowed) for allowed in self.allowed_paths):
                    return False
        except:
            # Return False if any exception occurs during path validation
            return False

        return True

    def execute_command(self, command: str) -> str:
        """Robust command execution with error handling"""
        try:
            # Execute the command using subprocess.run
            result = subprocess.run(
                command,
                shell=True,
                executable="/bin/bash",
                capture_output=True,
                text=True,
                timeout=15
            )
            # Return the command output or an error message
            return result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            # Return an error message if the command times out
            return "Error: Command timed out (15s limit)"
        except Exception as e:
            # Return an error message if any other exception occurs
            return f"Execution error: {str(e)}"

    def run_interface(self):
        """Improved interactive interface"""
        print("Natural Command Interface (type 'history' or 'exit')")
        while True:
            try:
                # Get user input
                user_input = input("\n> ").strip().lower()

                if user_input == 'history':
                    # Print command history
                    print("\nCommand History:")
                    for idx, cmd in enumerate(self.command_history, 1):
                        print(f"{idx}. {cmd}")
                    continue

                if user_input in ('exit', 'quit'):
                    # Exit the interface
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

                # Execute and store the command
                result = self.execute_command(command)
                print(f"\n{result}")
                self.command_history.append(command)

            except KeyboardInterrupt:
                # Handle keyboard interrupt
                print("\nExiting safely...")
                break
            except Exception as e:
                # Handle any other exceptions
                print(f"System error: {str(e)}")
                continue

if __name__ == "__main__":
    # Entry point of the script
    NaturalSystemInterface().run_interface()
