#!/usr/bin/env python3
"""
A simple help launcher for i3.

This script provides an interactive way to look up answers to common
questions about your i3 setup.  When invoked it presents a list of
topics via `rofi` or `dmenu`.  After you select a topic, it shows
the corresponding answer either using `rofi -e`, `xmessage`, or
falls back to printing to the terminal.  The help text is kept in
the `topics` dictionary below, so you can easily add more entries
to tailor it to your workflow.

To integrate this script with your i3 configuration, save it
somewhere in your `$PATH` (for example in `~/.config/i3/scripts/`)
and make it executable (`chmod +x i3_help.py`).  Then add a key
binding such as `bindsym $mod+F1 exec --no-startup-id path/to/i3_help.py`
to your `i3` config.  The window matching `title="i3_help"` is
configured as floating and sticky in the provided configuration,
ensuring that help messages never block your workflow.
"""

import os
import shutil
import subprocess
import sys
import yaml
import difflib
import datetime
import re


def choose_topic(topics):
    """Present the list of topics via rofi or dmenu and return the selection.

    Parameters
    ----------
    topics : list of str
        A list of question strings to display in the menu.

    Returns
    -------
    str or None
        The selected topic, or `None` if nothing was selected or
        rofi/dmenu could not be run.
    """
    menu_input = "\n".join(topics)
    # Determine which launcher to use.
    launcher_cmd = None
    # Prefer rofi if available; its `-dmenu` mode provides a nice UI
    if shutil.which("rofi"):
        launcher_cmd = ["rofi", "-dmenu", "-i", "-p", "i3 Help"]
    elif shutil.which("dmenu"):
        # `dmenu` is more basic but ubiquitous
        launcher_cmd = ["dmenu", "-p", "i3 Help"]
    else:
        return None
    try:
        result = subprocess.run(
            launcher_cmd,
            input=menu_input.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except FileNotFoundError:
        return None
    choice = result.stdout.decode("utf-8").strip()
    return choice if choice else None


def show_answer(answer):
    """Display the answer using an appropriate UI widget.

    Attempts to use rofi, xmessage, or notify-send to show the
    message.  If none of these programs are available, it falls
    back to printing to standard output.

    Parameters
    ----------
    answer : str
        The answer text to display.
    """
    if not answer:
        return
    # Prefer rich GUI dialogs if available
    # Try yad (Yet Another Dialog) first
    if shutil.which("yad"):
        try:
            subprocess.run([
                "yad",
                "--info",
                "--center",
                "--title=i3 Help",
                f"--text={answer}"
            ], check=False)
            return
        except FileNotFoundError:
            pass
    # Fallback to zenity
    if shutil.which("zenity"):
        try:
            subprocess.run([
                "zenity",
                "--info",
                "--no-wrap",
                "--text",
                answer,
                "--title=i3 Help",
            ], check=False)
            return
        except FileNotFoundError:
            pass
    # Use rofi's message dialog if rofi is present
    if shutil.which("rofi"):
        try:
            subprocess.run(["rofi", "-e", answer], check=False)
            return
        except FileNotFoundError:
            pass
    # Fallback to xmessage which opens a simple X11 dialog.  Use a
    # specific window title to trigger i3's floating/sticky rule.
    if shutil.which("xmessage"):
        try:
            subprocess.run(
                ["xmessage", "-center", "-title", "i3_help", answer], check=False
            )
            return
        except FileNotFoundError:
            pass
    # As another fallback, use notify-send to send a desktop notification.
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", "i3 Help", answer], check=False)
            return
        except FileNotFoundError:
            pass
    # Last resort: print to terminal
    sys.stdout.write(answer + "\n")
    sys.stdout.flush()


def load_topics_from_yaml() -> dict:
    """Load help topics from a YAML file.

    The YAML file should contain a list of mappings with `question`
    and `answer` keys.  Returns a dictionary mapping questions to
    answers.  If the file cannot be parsed or is missing, an empty
    dictionary is returned.
    """
    topics_file = os.path.join(os.path.dirname(__file__), "i3_help_topics.yaml")
    if not os.path.exists(topics_file):
        return {}
    try:
        with open(topics_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return {}
    if not isinstance(data, list):
        return {}
    # The YAML contains a list of entries with 'category', 'question' and 'answer'.
    topics_by_category = {}
    for entry in data:
        if isinstance(entry, dict) and "question" in entry and "answer" in entry:
            question = str(entry["question"]).strip()
            answer = str(entry["answer"]).rstrip()
            category = str(entry.get("category", "Misc")).strip()
            topics_by_category.setdefault(category, []).append((question, answer))
    return topics_by_category


def categorize_command(cmd: str) -> str:
    """Heuristically determine a category based on the command string."""
    lc = cmd.lower()
    # Check for workspace management first
    if "workspace" in lc or "move container to workspace" in lc:
        return "Workspaces"
    # Focus and movement
    if "focus" in lc or re.search(r"\bmove(\s+|-)\w*", lc):
        return "Focus & Movement"
    # Splitting and layout
    if "split" in lc or "layout" in lc:
        return "Splitting & Layout"
    # Floating / tiling
    if "floating" in lc or "tiling" in lc:
        return "Floating & Focus Modes"
    # Killing windows
    if "kill" in lc:
        return "Window Management"
    # Audio
    if "pactl" in lc or "pavucontrol" in lc:
        return "Audio"
    # Media controls
    if "playerctl" in lc:
        return "Media"
    # Brightness
    if "xbacklight" in lc or re.search(r"\blight\b", lc):
        return "Brightness"
    # Screenshots
    if "maim" in lc or "screenshot" in lc:
        return "Screenshots"
    # Lock / security
    if "i3lock" in lc:
        return "Lock & Security"
    # i3 management
    if any(k in lc for k in ["reload", "restart", "exit", "save-tree"]):
        return "i3 Management"
    return "Misc"


def extract_topics_from_config(config_path: str) -> dict:
    """Parse an i3 config file and produce help topics.

    Returns a dictionary mapping categories to a list of (question, answer)
    tuples.  Each bindsym line is turned into a generic question like
    "What does $mod+h do?".
    """
    topics_by_category: dict = {}
    if not config_path or not os.path.exists(config_path):
        return topics_by_category
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Look for bindsym lines: bindsym <keys> <command>
                if line.lower().startswith("bindsym"):
                    parts = line.split(None, 2)
                    if len(parts) < 3:
                        continue
                    key_combo = parts[1]
                    command = parts[2]
                    # Build question and answer
                    question = f"What does {key_combo} do?"
                    answer = f"The binding `{key_combo}` runs `{command}`."
                    category = categorize_command(command)
                    topics_by_category.setdefault(category, []).append((question, answer))
    except Exception:
        return topics_by_category
    return topics_by_category


def build_flat_index(topics_by_category: dict) -> dict:
    """Flatten category mapping into a question->answer dict."""
    flat = {}
    for cat, lst in topics_by_category.items():
        for q, a in lst:
            flat[q] = a
    return flat


def select_from_list(options: list, prompt: str) -> str:
    """Present a list of options via rofi/dmenu and return the selection."""
    menu_input = "\n".join(options)
    launcher_cmd = None
    if shutil.which("rofi"):
        # Use fuzzy matching in rofi for better searching
        launcher_cmd = ["rofi", "-dmenu", "-i", "-p", prompt, "-matching", "fuzzy"]
    elif shutil.which("dmenu"):
        launcher_cmd = ["dmenu", "-p", prompt]
    if launcher_cmd is None:
        # Fall back: simple text interface
        sys.stdout.write(f"{prompt}:\n")
        for i, opt in enumerate(options, 1):
            sys.stdout.write(f"{i}. {opt}\n")
        try:
            sel = int(input("Select a number (or 0 to cancel): "))
        except Exception:
            return None
        if 1 <= sel <= len(options):
            return options[sel - 1]
        return None
    # Use rofi/dmenu
    try:
        result = subprocess.run(
            launcher_cmd,
            input=menu_input.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        selection = result.stdout.decode("utf-8").strip()
        return selection if selection else None
    except FileNotFoundError:
        return None


def prompt_search_query() -> str:
    """Prompt the user for a search query via rofi/dmenu."""
    launcher_cmd = None
    if shutil.which("rofi"):
        launcher_cmd = ["rofi", "-dmenu", "-i", "-p", "Search i3 help"]
    elif shutil.which("dmenu"):
        launcher_cmd = ["dmenu", "-p", "Search i3 help"]
    if launcher_cmd is None:
        try:
            return input("Search i3 help: ").strip()
        except Exception:
            return ""
    try:
        result = subprocess.run(
            launcher_cmd,
            input="".encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.stdout.decode("utf-8").strip()
    except FileNotFoundError:
        return ""


def fuzzy_search(questions: list, query: str, max_results: int = 5) -> list:
    """Return a list of up to max_results questions closest to the query."""
    if not query:
        return []
    matches = difflib.get_close_matches(query, questions, n=max_results, cutoff=0.1)
    return matches


def log_usage(question: str):
    """Append the used question to a log file with a timestamp."""
    try:
        log_dir = os.path.expanduser("~/.config/i3")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "i3_help.log")
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
            f.write(f"{timestamp}\t{question}\n")
    except Exception:
        pass


def main():
    topics_by_category = load_topics_from_yaml()
    if not topics_by_category:
        # If no external topics are found, we cannot proceed with categories.
        # Fall back to the previous implementation: build a small dictionary
        flat_topics = {
            "How do I change audio output?": (
                "To switch audio devices you can use the dedicated keybindings.\n"
                "• Press $mod+F9 to set your USB audio device as the default sink.\n"
                "• Press $mod+F8 to switch back to the internal audio output.\n"
                "• Press $mod+Shift+a to launch the PulseAudio volume control (pavucontrol)\n"
                "  where you can pick any available output device.\n\n"
                "These bindings come from your i3 configuration where they call `pactl` to\n"
                "set the default sink and send a desktop notification【708996610248841†L310-L323】."
            ),
            "How do I restart i3?": (
                "To restart i3 without ending your session press $mod+Shift+r.\n"
                "This triggers the `restart` command which reloads i3 in‑place while\n"
                "preserving your layout【708996610248841†L440-L456】.  It's useful when you\n"
                "edit your configuration and want to apply the changes immediately.\n"
            ),
        }
        question_list = list(flat_topics.keys())
        choice = choose_topic(question_list)
        if not choice:
            return
        answer = flat_topics.get(choice)
        if answer:
            show_answer(answer)
            log_usage(choice)
        return
    # Attempt to parse the user's i3 configuration and merge topics
    # Look for possible config locations.  The primary path is the user's
    # i3 config in ~/.config/i3/config.  As a fallback for this demo,
    # also check a config file in the same directory as this script.
    config_paths = [os.path.expanduser("~/.config/i3/config"), os.path.join(os.path.dirname(__file__), "config")]
    for cfg in config_paths:
        extracted = extract_topics_from_config(cfg)
        for cat, qas in extracted.items():
            # Avoid duplicates when merging
            existing_qs = {q for q, _ in topics_by_category.get(cat, [])}
            for q, a in qas:
                if q not in existing_qs:
                    topics_by_category.setdefault(cat, []).append((q, a))
    # Build a flat index for search
    flat_topics = build_flat_index(topics_by_category)
    questions = list(flat_topics.keys())
    # Build category menu; add search option
    categories = sorted(topics_by_category.keys())
    menu_options = categories + ["Search..."]
    cat_choice = select_from_list(menu_options, "i3 Help")
    if not cat_choice:
        return
    # If search selected, prompt for query and perform fuzzy search
    if cat_choice == "Search...":
        query = prompt_search_query()
        matches = fuzzy_search(questions, query)
        if not matches:
            # No matches; inform user
            show_answer("No topics matched your search.")
            return
        question_choice = select_from_list(matches, "Matches")
        if not question_choice:
            return
        answer = flat_topics.get(question_choice)
        if answer:
            show_answer(answer)
            log_usage(question_choice)
        return
    # Otherwise, browse selected category
    topic_list = [q for q, _ in topics_by_category.get(cat_choice, [])]
    question_choice = select_from_list(topic_list, cat_choice)
    if not question_choice:
        return
    answer = flat_topics.get(question_choice)
    if answer:
        show_answer(answer)
        log_usage(question_choice)


if __name__ == "__main__":
    main()