import asyncio
import traceback
from urllib.parse import urlparse, unquote

import streamlit as st

from main import run_workflow


st.title("AI Code Generator")

st.write(
    "Enter the GitHub project URL and coding instruction."
)


repository_url = st.text_input(
    "GitHub Project URL",
    placeholder=(
        "https://github.com/owner/repository/"
        "tree/main/folder"
    )
)


instruction = st.text_input(
    "Coding Instruction",
    placeholder=(
        "Example: Change the output filename "
        "to converted.png."
    )
)


if st.button("Generate Code"):

    if not repository_url.strip():

        st.warning(
            "Please enter the GitHub project URL."
        )

    elif not instruction.strip():

        st.warning(
            "Please enter a coding instruction."
        )

    else:

        try:

            # Parse GitHub URL
            parsed_url = urlparse(
                repository_url.strip()
            )

            parts = [
                unquote(part)
                for part in parsed_url.path
                .strip("/")
                .split("/")
                if part
            ]

            # Check minimum URL structure
            if len(parts) < 2:

                st.error(
                    "Invalid GitHub repository URL."
                )

            else:

                # Repository information
                owner = parts[0]
                repo = parts[1]

                # Default project path
                project_path = "/"

                # Expected format:
                #
                # /owner/repository/tree/branch/project/path
                #
                if (
                    len(parts) >= 5
                    and parts[2] == "tree"
                ):

                    # parts[3] = branch
                    # parts[4:] = project path

                    project_path = "/".join(
                        parts[4:]
                    )

                else:

                    st.error(
                        "Please enter a GitHub project URL "
                        "using the format:"
                    )

                    st.code(
                        "https://github.com/owner/"
                        "repository/tree/main/folder"
                    )

                    st.stop()

                with st.spinner(
                    "Generating and evaluating code..."
                ):

                    results = asyncio.run(
                        run_workflow(
                            instruction,
                            owner,
                            repo,
                            project_path
                        )
                    )

                st.session_state["results"] = results

        except Exception as error:

            st.error(
                f"Error during code generation: {error}"
            )

            st.code(
                traceback.format_exc()
            )


# Display results
if "results" in st.session_state:

    results = st.session_state["results"]

    for result in results:

        st.subheader(
            f"Attempt {result['attempt']}"
        )

        st.write(
            f"Score: {result['score']}/100"
        )

        st.write(
            f"Status: {result['status']}"
        )

        st.text_area(
            "Generated Code",
            result["code"],
            height=400,
            key=f"code_{result['attempt']}"
        )

        st.write("Feedback:")

        st.write(
            result["feedback"]
        )

        if result["improved_instruction"]:

            st.write(
                "Improved Instruction:"
            )

            st.info(
                result["improved_instruction"]
            )

    if results[-1]["status"].upper() == "PASS":

        st.success(
            "Code generated successfully!"
        )

    else:

        st.error(
            "Code generation failed after "
            "maximum attempts."
        )