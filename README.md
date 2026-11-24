AI Code Generator

Project Overview

AI Code Generator is an AI-powered application that generates and evaluates Python code based on user instructions. It uses repository context through MCP tools to understand existing project files and generate relevant code.

Technologies Used

- Python
- PydanticAI
- MCP (Model Context Protocol)
- Ollama
- Streamlit

Project Workflow

1. User Instruction: User provides the coding requirement.
2. MCP Integration: Retrieves relevant repository files and their contents.
3. Code Generator: Generates code using the user instruction and repository context.
4. Code Evaluator: Evaluates the generated code.
5. Retry Mechanism: If the code fails evaluation, it goes back for improvement.
6. Instruction Generator: Generates instructions for the final output.
7. Final Output: Provides the evaluated code to the user.

Key Features

- AI-based code generation.
- Repository file retrieval using MCP.
- Context-aware code generation.
- Automated code evaluation.
- Retry mechanism for improving generated code.
- Streamlit-based user interface.

Application Architecture

User Instruction → MCP → Code Generator → Code Evaluator → Retry / Pass → Instruction Generator → Final Output

How to Run

1. Clone this repository.
2. Install the required dependencies.
3. Configure the Ollama model and endpoint.
4. Run the application using Streamlit.

pip install -r requirements.txt
streamlit run app.py

Project Objective

To simplify software development by generating context-aware code and improving its quality through an automated evaluation and retry workflow.# AI_Code_Generator
