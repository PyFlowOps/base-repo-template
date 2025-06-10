import argparse
import json
import os
import subprocess

from icecream import ic

BASE = os.path.dirname(
    os.path.abspath(__file__)
)  # Get the base directory of the script

REPO = os.path.abspath(
    os.path.join(BASE, "..", "..", "..")
)  # Get the repository directory

ic.disable()  # Disable icecream output by default

if not os.environ.get("GITHUB_REPOSITORY"):
    print("[ERROR] - The GITHUB_REPOSITORY environment variable is not set.")
    exit(1)

parser = argparse.ArgumentParser(
    description="Update the version from the registrant."
)
parser.add_argument(
    "--version",
    type=str,
    help="The version to set in the registrant file, i.e. ~> pfo.json, pyproject.toml.",
)
parser.add_argument(
    "--debug",
    action="store_true",
    help="Enable debug mode.",
)

args = parser.parse_args()

if args.debug:
    ic.enable()

if not args.version:
    print("[ERROR] - The version argument (from registrant) is required.")
    exit(1)


def get_github_releases() -> json:
    """Get the latest release version from GitHub.

    Returns:
        str: The latest release version.
    """
    cmd = [
        "gh",
        "release",
        "list",
        "--json",
        "isDraft,isLatest,isPrerelease,name,tagName",
    ]
    result = subprocess.run(cmd, check=True, capture_output=True)
    if result.returncode != 0:
        print(f"[ERROR] - {result.stderr.decode('utf-8')}")
        exit(1)

    return json.loads(result.stdout.decode("utf-8").strip())


def _set_release_versions(_latest_data: json) -> tuple:
    """Set the release versions based on the latest data.

    Args:
        _latest_data (json): The latest release data.

    Returns:
        tuple: A tuple containing the release version, prerelease version, and draft version.
    """
    # Set the below lists to populate
    _rel_data = []
    _pre_data = []
    _dft_data = []

    # Latest Release Information
    for i in _latest_data:
        if i["isDraft"]:
            _dft_data.append(i)
        elif i["isPrerelease"]:
            _pre_data.append(i)
        elif i["isLatest"]:
            _rel_data.append(i)

    # Let's ensure that there are not more than one release of each type
    if len(_rel_data) > 1:
        print("[ERROR] - There are more than one release that is marked as latest.")
        exit(1)

    if len(_pre_data) > 1:
        print("[ERROR] - There are more than one release that is marked as prerelease.")
        exit(1)

    if len(_dft_data) > 1:
        print("[ERROR] - There are more than one release that is marked as draft.")
        exit(1)

    if _rel_data:
        _rv = _rel_data[0]["tagName"].lstrip("v")  # Remove the leading 'v' if present
    else:
        _rv = None

    if _pre_data:
        _prv = _pre_data[0]["tagName"].lstrip("v")  # Remove the leading 'v' if present
    else:
        _prv = None

    if _dft_data:
        _dft = _dft_data[0]["tagName"].lstrip("v")  # Remove the leading 'v' if present
    else:
        _dft = None

    return (_rv, _prv, _dft)


def _compare_versions(
    version_type: str, version_to_compare: tuple, new_version: tuple
) -> None:
    """At the very least, each digit should AT LEAST be equal to the current version.
    Args:
        version_to_compare (tuple): The the version to compare as a tuple of integers to the _new_version.
        new_version (tuple): The new version as a tuple of integers.
    Raises:
        ValueError: If the new version is less than the current version.
    """
    ic(
        f"_compare_versions() - The new version {new_version} is being compared to the {version_type} version {version_to_compare}."
    )
    for i in range(len(new_version)):
        if not new_version[i] >= version_to_compare[i]:
            raise ValueError(
                f"The new version {new_version} is less than the {version_type} version {version_to_compare}."
            )

    ic(f"_compare_versions() - {version_type} - success.")


def __should_be_equal(version_to_compare: tuple, new_version: tuple) -> bool:
    """Check if the current version and new version are equal.

    Args:
        version_to_compare (tuple): The current version as a tuple of integers.
        new_version (tuple): The new version as a tuple of integers.

    Returns:
        bool: True if the versions are equal, False otherwise.
    """
    for i in range(len(new_version)):
        if new_version[i] != version_to_compare[i]:
            print(
                f"[ERROR] - The new version {new_version} and current version {version_to_compare} SHOULD be equal."
            )
            return False

    ic(
        f"__should_be_equal() - The new version {new_version} and current version {version_to_compare} are equal."
    )
    return True


def __should_be_greater(version_to_compare: tuple, new_version: tuple) -> bool:
    """Check if the new version is greater than the current version.

    Args:
        version_to_compare (tuple): The the version to compare as a tuple of integers to the _new_version.
        new_version (tuple): The new version as a tuple of integers.

    Returns:
        bool: True if the new version is greater, False otherwise.
    """
    ic(
        f"__should_be_greater() - The new version {new_version} is being compared to the current version {version_to_compare}."
    )
    gt = False
    assert len(new_version) == 3, "The new version must be a tuple of 3 integers."
    assert (
        len(version_to_compare) == 3
    ), "The version to compare must be a tuple of 3 integers."

    for i in range(0, len(new_version)):
        ic(f"__should_be_greater() - Iterative -- {i}")
        if i == 0:
            ic("Comparing the major version...")
            # Let's check if the index is 0, this is the major version - meaning if this is greater, then the minor and patch versions MUST be 0
            if new_version[i] > version_to_compare[i]:
                ic(
                    f"__should_be_greater() - The major version is being compared. {new_version[i]} > {version_to_compare[i]}"
                )
                # This is the major version, so we need to check if the minor and patch versions are 0
                if new_version[1] != 0 or new_version[2] != 0:
                    print(
                        f"[ERROR] - The new version {new_version} is greater than the current version {version_to_compare}, but the minor and patch versions are not 0."
                    )
                    print(
                        "[CRITICAL] - If the major version has changed, the minor and patch versions must be 0."
                    )
                    exit(1)

                gt = True
                break  # We found the new version is greater

        if i == 1:
            ic("Comparing the minor version...")
            # This is the minor version, so we need to check if the patch version is 0
            if new_version[i] > version_to_compare[i]:
                ic(
                    f"__should_be_greater() - The minor version is being compared. {new_version[i]} > {version_to_compare[i]}"
                )
                if new_version[2] != 0:
                    print(
                        f"[ERROR] - The new version {new_version} is greater than the current version {version_to_compare}, but the patch version is not 0."
                    )
                    print(
                        "[CRITICAL] - If the minor version has changed, the patch version must be 0."
                    )
                    exit(1)

                gt = True
                break  # We found the new version is greater

        if i == 2:
            ic("Comparing the patch version...")
            # This is the patch version, so we need to check if the patch version is greater
            ic(
                f"__should_be_greater() - The patch version is being compared. {new_version[i]} > {version_to_compare[i]}"
            )
            if new_version[i] > version_to_compare[i]:
                gt = True
                break

    if not gt:
        ic("The versions are equal...")
        return False

    ic(
        f"__should_be_greater() - The new version {new_version} is greater than the current version {version_to_compare}."
    )
    return True


def __draft_greater_than_prerelease(dft: tuple, prv: tuple) -> bool:
    """Check if the draft version is greater than the prerelease version.

    Args:
        dft (tuple): The draft version as a tuple of integers.
        prv (tuple): The prerelease version as a tuple of integers.
    Returns:
        bool: True if the draft version is greater than the prerelease version, False otherwise.
    """
    gt = False
    for i in range(len(dft)):
        if dft[i] > prv[i]:
            gt = True
            break  # We found the draft version is greater

    if not gt:
        print(
            f"[ERROR] - The draft version {dft} is not greater than the prerelease version {prv}."
        )
        return False

    ic(
        f"[INFO] - _draft_greater_than_prerelease() - The draft version {dft} is greater than the prerelease version {prv}."
    )
    return True


def __draft_greater_than_release(dft: tuple, rv: tuple) -> bool:
    """Check if the draft version is greater than the release version.

    Args:
        dft (tuple): The draft version as a tuple of integers.
        rv (tuple): The release version as a tuple of integers.
    Returns:
        bool: True if the draft version is greater than the release version, False otherwise.
    """
    gt = False
    for i in range(len(dft)):
        if dft[i] > rv[i]:
            gt = True
            break  # We found the draft version is greater

    if not gt:
        print(
            f"[ERROR] - The draft version {dft} is not greater than the release version {rv}."
        )
        return False

    ic(
        f"[INFO] - _draft_greater_than_release() - The draft version {dft} is greater than the release version {rv}."
    )
    return True


if __name__ == "__main__":
    _new_version = tuple(
        [int(i) for i in args.version.lstrip("v").split(".")]
    )  # Remove the leading 'v' if present -- NOTE: This is from the pyproject.toml file
    _latest_data = get_github_releases()

    # Get the latest release version(s)
    _tupledata = _set_release_versions(_latest_data)

    # Let's set the release versions
    # These are just the version numbers, not the full tag name from github --> i.e.~> 2.3.4 NOT v2.3.4
    _rv = (
        tuple([int(i) for i in _tupledata[0].split(".")]) if _tupledata[0] else None
    )  # Latest release version
    _prv = (
        tuple([int(i) for i in _tupledata[1].split(".")]) if _tupledata[1] else None
    )  # Prerelease version
    _dft = (
        tuple([int(i) for i in _tupledata[2].split(".")]) if _tupledata[2] else None
    )  # Draft version

    ### DEBUGGING ###
    # _rv = None # This is the current release version that we are working on
    # _prv = None # This is the current draft version that we are working on
    # _dft = None # This is the current draft version that we are working on
    ### DEBUGGING ###

    ic(f"Current Draft Version: {_dft}")
    ic(f"Current Prerelease Version: {_prv}")
    ic(f"Current Release Version: {_rv}")

    # Compare the versions
    if not _prv and not _rv:
        ic("No release or prerelease version found.")
        ic("We will start at 0.1.0")
        if _dft is None:
            if _new_version != (0, 1, 0):
                print(
                    "[ERROR] - This is the first Draft Release for this project, it must be - 0.1.0."
                )
                exit(1)

            if _new_version == (0, 1, 0):
                ic(
                    "This is the first Draft Release for this project, it is set to - 0.1.0."
                )
                print(f"{args.version.lstrip('v')}")
                exit(0)

    if _prv:
        ic("PRERELEASE FOUND")
        ic(
            "We have a current prerelease version set, running this logic block -- if _prv: do something"
        )
        # Run a basic comparison, must be AT LEAST equal to the current prerelease version
        _compare_versions(
            version_type="prerelease", version_to_compare=_prv, new_version=_new_version
        )  # This will raise an error if the new version is less than the current prerelease version

        if _dft:
            ic("PRERELEASE FOUND && DRAFT FOUND")
            # Run a basic comparison, must be AT LEAST equal to the current draft version
            _compare_versions(
                version_type="draft release",
                version_to_compare=_dft,
                new_version=_new_version,
            )

            # If there is a current draft, they should be equal
            if not __should_be_equal(version_to_compare=_dft, new_version=_new_version):
                print(
                    "[ERROR] - The new version is not equal to the current draft version - If there is a current draft, the new draft version MUST be the same."
                )
                exit(1)
        else:
            ic("PRERELEASE FOUND && DRAFT NOT FOUND")
            # If there is no current draft, the new version must be greater than the prerelease version
            if not __draft_greater_than_prerelease(dft=_new_version, prv=_prv):
                print(
                    "[ERROR] - The new version is not greater than the current prerelease version - If there is no current draft, the new draft version MUST be higher."
                )
                exit(1)
    else:
        ic("PRERELEASE NOT FOUND")
        if _dft:
            ic("PRERELEASE NOT FOUND && DRAFT FOUND")
            ic(
                "We have a current draft version set, running this logic block -- if _dft: do something"
            )

            # Run a basic comparison, must be AT LEAST equal to the current draft version
            _compare_versions(
                version_type="draft release",
                version_to_compare=_dft,
                new_version=_new_version,
            )  # This will raise an error if the new version is less than the current draft version

            if not __should_be_equal(version_to_compare=_dft, new_version=_new_version):
                print(
                    "[ERROR] - The new draft version is not equal to the current draft version - If there is a current draft, the versions MUST be the same."
                )
                exit(1)

            ic(
                "The new version is equal to the current draft version. This is expected and correct..."
            )
        else:
            ic("PRERELEASE NOT FOUND && DRAFT NOT FOUND")
            # If there is no current draft, the new version must be greater than the release version
            if not __draft_greater_than_release(dft=_new_version, rv=_rv):
                print(
                    "[ERROR] - The new version is not greater than the current release version - If there is no current draft, or prerelease, the new draft version MUST be higher than the latest release."
                )
                exit(1)

    if not __should_be_greater(version_to_compare=_rv, new_version=_new_version):
        print(
            "[ERROR] - The new version is not greater than the current release version - If there is a current release, the new draft version MUST be higher."
        )
        exit(1)

    # Let's print the new version for tagging purposes (not a tuple)
    print(f"{args.version.lstrip('v')}")
