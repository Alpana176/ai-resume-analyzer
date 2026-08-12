import json
import os


def save_to_json(new_data):

    # ---------------------------------------------------------
    # Project root
    # ---------------------------------------------------------

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


    # ---------------------------------------------------------
    # Data directory
    # ---------------------------------------------------------

    data_dir = os.path.join(
        base_dir,
        "data"
    )

    os.makedirs(
        data_dir,
        exist_ok=True
    )


    filename = os.path.join(
        data_dir,
        "resume_data.json"
    )


    # ---------------------------------------------------------
    # Load existing data
    # ---------------------------------------------------------

    data = []

    if os.path.exists(filename):

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as f:

                existing_data = json.load(f)

                if isinstance(
                    existing_data,
                    list
                ):

                    data = existing_data

        except (
            json.JSONDecodeError,
            OSError
        ):

            data = []


    # ---------------------------------------------------------
    # Append new result
    # ---------------------------------------------------------

    data.append(
        new_data
    )


    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


    print(
        "✅ Analysis saved at:",
        filename
    )