# Natural Language System Interface

A robust and secure natural language interface for executing Linux commands, designed to ensure valid command generation and execution while prioritizing system safety.

![image](https://github.com/user-attachments/assets/290b9db9-c500-49aa-b722-199875dfc189)


## Features

- Natural language to Linux command conversion using the **Ollama Llama** model.
- Fine-tuned **Llama 3.1** model for generating Linux commands over **Ollama** running on the local system.
- Enhanced security with safety rules to block destructive commands.
- Path validation to restrict file operations to safe directories.
- Command history tracking.
- User confirmation for destructive operations.
- Interactive command-line interface with graceful exit.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Security Features](#security-features)
- [Example Commands](#example-commands)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8 or higher

- Install Ollama locally:

  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

- Authenticate with Hugging Face:

  ```bash
  huggingface-cli login
  ```

  Follow the instructions to enter your Hugging Face token.

- Pull the custom model using Ollama:

  ```bash
  ollama run hf.co/your-username/your-custom-model:Q8_0
  ```

### Clone the Repository

```bash
git clone https://github.com/HarshaLakkaraju/Natural_Language_System_Interface_Linux
cd Natural_Language_System_Interface_Linux
```

### Install Requirements

Install the required package using `pip`:

```bash
pip install -r req.txt
```

> Note: Ensure that the **Ollama API** is running locally at `http://localhost:11434`.

## Usage

Run the program using:

```bash
python main.py
```

### Interactive Commands

- Type natural language commands like `list files` or `show documents`.
- Use the following special commands:
  - `history`: View the command history.
  - `exit` or `quit`: Safely exit the program.

## Security Features

- **Blocked Commands:** Prevents execution of destructive commands, such as:
  - `rm -rf`
  - `mkfs`
  - Commands with `sudo`, `poweroff`, `reboot`
- **Path Validation:** Restricts file operations to safe directories (`~/Documents`, `~/Downloads`, and `/tmp`).
- **Confirmation for Destructive Operations:** Asks for confirmation before executing commands like `rm`, `mv`, or `cp`.

## Example Commands

Here are some example prompts and their corresponding outputs:

| Prompt           | Generated Command |
| ---------------- | ----------------- |
| `list files`     | `ls -l`           |
| `show documents` | `ls ~/Documents`  |

## License

This project is licensed under the MIT License.

