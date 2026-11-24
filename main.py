import json

from pydantic_ai import Agent

from github_mcp import (
    list_repository_files,
    get_repository_file
)

from code_generator import code_generator
from code_evaluator import code_evaluator
from instruction_generator import instruction_generator
from llm import model


MAX_RETRIES = 3


# ---------------------------------------------------------
# File Selector
# ---------------------------------------------------------

file_selector = Agent(
    model,
    output_type=str,
    system_prompt="""
You are a repository file selector.

Select the single most relevant source code file
from the provided project files based on the user's
coding instruction.

Requirements:

1. Select only one file.
2. Return only the exact file path.
3. Do not return explanations.
4. Do not return Markdown.
5. Do not invent a file path.
6. Select only a file that exists in the provided list.
"""
)


# ---------------------------------------------------------
# Get Directory Contents
# ---------------------------------------------------------

async def get_directory_contents(
    owner,
    repo,
    path
):

    result = await list_repository_files(
        owner,
        repo,
        path
    )

    try:

        data = json.loads(result)

        return data

    except json.JSONDecodeError:

        return result


# ---------------------------------------------------------
# Get Project Files
# ---------------------------------------------------------

async def get_project_files(
    owner,
    repo,
    path
):

    project_files = {}

    contents = await get_directory_contents(
        owner,
        repo,
        path
    )

    # If MCP returns a JSON string
    if isinstance(contents, str):

        try:

            contents = json.loads(contents)

        except json.JSONDecodeError:

            return project_files


    if not isinstance(contents, list):

        return project_files


    for item in contents:

        if not isinstance(item, dict):

            continue


        item_type = item.get(
            "type"
        )

        item_path = item.get(
            "path"
        )

        if not item_path:

            continue


        # Skip unnecessary directories
        if item_type == "dir":

            folder_name = item_path.split("/")[-1]

            if folder_name in [
                "__pycache__",
                "output",
                "fonts"
            ]:

                continue


            nested_files = await get_project_files(
                owner,
                repo,
                item_path
            )

            project_files.update(
                nested_files
            )


        # Source files
        elif item_type == "file":

            source_extensions = (
                ".py",
                ".js",
                ".ts",
                ".java",
                ".cpp",
                ".c"
            )

            if item_path.endswith(
                source_extensions
            ):

                project_files[item_path] = ""


    return project_files


# ---------------------------------------------------------
# Run Workflow
# ---------------------------------------------------------

async def run_workflow(
    instruction,
    owner,
    repo,
    project_path
):

    results = []


    # -----------------------------------------------------
    # Step 1: Get files from selected project
    # -----------------------------------------------------

    project_files = await get_project_files(
        owner,
        repo,
        project_path
    )


    if not project_files:

        raise RuntimeError(
            "No source code files were found in the "
            "selected GitHub project."
        )


    # -----------------------------------------------------
    # Step 2: Select relevant file
    # -----------------------------------------------------

    file_selection_prompt = f"""
User instruction:

{instruction}


Selected project:

{project_path}


Available source files:

{list(project_files.keys())}


Select the single most relevant file for implementing
the user's instruction.

Return only the exact file path.
"""


    result = await file_selector.run(
        file_selection_prompt
    )


    selected_path = result.output.strip()


    # Remove Markdown formatting if model adds it
    selected_path = selected_path.strip(
        "`"
    )


    if selected_path not in project_files:

        raise RuntimeError(
            f"File selector returned an invalid file path: "
            f"{selected_path}"
        )


    # -----------------------------------------------------
    # Step 3: Get original file code
    # -----------------------------------------------------

    original_code = await get_repository_file(
        owner,
        repo,
        selected_path
    )


    current_instruction = instruction


    # -----------------------------------------------------
    # Step 4: Generate → Evaluate → Improve
    # -----------------------------------------------------

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):


        # -------------------------------------------------
        # Code Generator
        # -------------------------------------------------

        generator_prompt = f"""
Original user instruction:

{current_instruction}


Selected project:

{project_path}


Selected file:

{selected_path}


Original code:

{original_code}


Generate the complete updated source code.

Requirements:

1. Follow the instruction exactly.

2. Use the original code as the source of truth.

3. Preserve existing functionality.

4. Modify only what is necessary.

5. Preserve existing imports, data structures,
   variable types, function names, function interfaces,
   and program structure unless the instruction
   specifically requires changing them.

6. Do not remove functionality that was not requested.

7. Return the COMPLETE updated source code.

8. Do not return a code fragment.

9. Do not return Markdown code fences.

10. Do not return a placeholder.

11. Do not return an empty code field.

12. Return a short explanation of the changes.

Actually implement the requested change in the
provided code.
"""


        result = await code_generator.run(
            generator_prompt
        )


        generated_code = result.output.code

        explanation = result.output.explanation


        # -------------------------------------------------
        # Code Evaluator
        # -------------------------------------------------

        evaluator_prompt = f"""
Original user instruction:

{current_instruction}


Selected file:

{selected_path}


Original code:

{original_code}


Generated code:

{generated_code}


Evaluate the generated code.

Check:

1. Whether the user's instruction was implemented.

2. Whether existing functionality is preserved.

3. Whether unnecessary changes were made.

4. Whether imports, data structures, variable types,
   function interfaces, and program structure were
   unnecessarily changed.

5. Whether there are obvious logical or implementation
   problems.

Set status to PASS only if the requested change is
actually implemented and the existing functionality is
adequately preserved.

Return:

- score: 0 to 100
- status: PASS or FAIL
- feedback: Clear explanation

Do not rewrite the code.
"""


        evaluation = await code_evaluator.run(
            evaluator_prompt
        )


        score = evaluation.output.score

        status = evaluation.output.status

        feedback = evaluation.output.feedback


        # -------------------------------------------------
        # PASS
        # -------------------------------------------------

        if status.upper() == "PASS":

            results.append(
                {
                    "attempt": attempt,
                    "instruction": current_instruction,
                    "code": generated_code,
                    "score": score,
                    "status": status,
                    "feedback": feedback,
                    "improved_instruction": ""
                }
            )


            return results


        # -------------------------------------------------
        # FAIL
        # -------------------------------------------------

        improved_instruction = ""


        if attempt < MAX_RETRIES:


            instruction_prompt = f"""
Original user instruction:

{instruction}


Selected project:

{project_path}


Selected file:

{selected_path}


Original code:

{original_code}


Generated code:

{generated_code}


Evaluator score:

{score}


Evaluator status:

{status}


Evaluator feedback:

{feedback}


Create an improved instruction for the Code Generator.

The Code Generator only receives:

- the selected file
- the original code
- the improved instruction

Therefore:

1. Focus only on the selected file.

2. Do not ask the Code Generator to search the
   repository.

3. Do not ask it to modify other files.

4. Preserve the user's original intent.

5. Tell the Code Generator exactly what needs
   to be fixed.

6. Preserve existing functionality.

7. Preserve existing imports, data structures,
   variable types, function interfaces, and program
   structure unless the instruction specifically
   requires changing them.

8. Modify only what is necessary.

9. If the previous code did not actually implement
   the requested change, explicitly tell the Code
   Generator to implement that change directly.

10. If unnecessary changes were made, explicitly
    tell the Code Generator to revert those changes.

Return only the improved instruction.
"""


            instruction_result = (
                await instruction_generator.run(
                    instruction_prompt
                )
            )


            improved_instruction = (
                instruction_result.output.instruction
            )


            current_instruction = (
                improved_instruction
            )


        # -------------------------------------------------
        # Store Attempt
        # -------------------------------------------------

        results.append(
            {
                "attempt": attempt,
                "instruction": current_instruction,
                "code": generated_code,
                "score": score,
                "status": status,
                "feedback": feedback,
                "improved_instruction": improved_instruction
            }
        )


    # -----------------------------------------------------
    # Return after maximum attempts
    # -----------------------------------------------------

    return results