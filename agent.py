"""
Contact Management Bot

A simple command-line bot for managing contacts with phone numbers.
Supports adding, updating, retrieving, and listing contacts with validation.
"""

import re
from colorama import Fore, Style
from tabulate import tabulate

IDENT = " "
BOT_COLOR = Fore.YELLOW
BOT_ERROR_COLOR = Fore.RED
HELP_MAIN_TEXT = Fore.LIGHTGREEN_EX

COMMANDS_HELP_INFO = {
    "hello": f"{HELP_MAIN_TEXT}{BOT_COLOR}'hello' {HELP_MAIN_TEXT}just to get nice greeting :){Style.RESET_ALL}",
    "add": f"{HELP_MAIN_TEXT}{BOT_COLOR}'add <username> <phone number>' {HELP_MAIN_TEXT}to add user with it's phone.'{Style.RESET_ALL}",
    "change": f"{HELP_MAIN_TEXT}{BOT_COLOR}'change <username> <phone number>' {HELP_MAIN_TEXT}to update username's phone.'{Style.RESET_ALL}",
    "phone": f"{HELP_MAIN_TEXT}{BOT_COLOR}'phone <username>' {HELP_MAIN_TEXT}to get phone of the user.{Style.RESET_ALL}",
    "all": f"{HELP_MAIN_TEXT}{BOT_COLOR}'all' {HELP_MAIN_TEXT}to get get list of all users and their phones{Style.RESET_ALL}",
    "exit or close": f"{HELP_MAIN_TEXT}{BOT_COLOR}'close' or 'exit' {HELP_MAIN_TEXT} to stop the assistant.{Style.RESET_ALL}",
}

FUNC_COMMAND_MAP = {
    "add_contact": "add",
    "update_contact": "change",
    "get_users_phone": "phone",
}

ERR_NAME_AND_PHONE = "Give me name and phone please."

USERS = {}


def parse_input(user_input):
    """
    Parse user input into command and arguments.
    Handles empty input gracefully.

    Returns:
        tuple: (command, args) where command is lowercase string and args is list
    """
    parts = user_input.split()
    if not parts:
        return "", []
    cmd, *args = parts
    cmd = cmd.strip().lower()
    return cmd, args


def print_error(message):
    """
    Print error message with consistent formatting.

    Args:
        message: Error message to display
    """
    print(f"{IDENT}{BOT_ERROR_COLOR}{message}{Style.RESET_ALL}")


def print_success(message):
    """
    Print success message with consistent formatting.

    Args:
        message: Success message to display
    """
    print(f"{IDENT}{BOT_COLOR}{message}{Style.RESET_ALL}")


def print_dict_as_list(dictionary: dict, headers: list):
    """
    Print dictionary items as a formatted list.

    Args:
        dictionary: Dictionary to display with key-value pairs
    """
    if not dictionary:
        print_error(f"There is no records yet.")
        return
    print(f"{tabulate(dictionary.items(), headers=headers, tablefmt='rounded_outline')}")


def validate_phone(phone: str) -> None:
    """
    Validate phone number format, raising ValueError if invalid.

    Phone must contain 10-15 digits (ignoring formatting characters
    like spaces, hyphens, parentheses, plus signs, and periods).

    Args:
        phone: Phone number string to validate

    Raises:
        ValueError: If the phone format is invalid.
    """
    cleaned = re.sub(r"[\s\-\(\)\+\.]", "", phone)
    if not (cleaned.isdigit() and 10 <= len(cleaned) <= 15):
        raise ValueError(
            f"Phone '{phone}' is not matching valid format. "
            "Should be digits only, 10 to 15 length."
        )


def input_error(func):
    """
    Decorator that handles input errors for command handler functions.

    Catches ValueError, KeyError, and IndexError, returning a formatted error
    message in BOT_ERROR_COLOR. For usage errors (wrong arg count, missing
    username) it also appends the command format hint from COMMANDS_HELP_INFO.

    Args:
        func: Command handler function to wrap.

    Returns:
        Wrapped function that returns an error string instead of raising.
    """

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            cmd_key = FUNC_COMMAND_MAP.get(func.__name__)
            is_usage_error = (
                isinstance(e, IndexError) or e.args[0] == ERR_NAME_AND_PHONE
            )
            hint = (
                f"\n{COMMANDS_HELP_INFO[cmd_key]}"
                if (cmd_key and is_usage_error)
                else ""
            )
            return f"{IDENT}{BOT_ERROR_COLOR}{e.args[0]}{Style.RESET_ALL}" + hint

    return inner


@input_error
def add_contact(args):
    """
    Add a new contact to the USERS dict.

    Args:
        args: List of [username, phone]. Must contain exactly 2 items.

    Returns:
        str: Formatted success message, or None if the user already exists.

    Raises:
        ValueError: If args count != 2 or phone format is invalid.
    """
    if len(args) != 2:
        raise ValueError(ERR_NAME_AND_PHONE)
    name, phone = args

    username = name.capitalize()

    validate_phone(phone)

    if username in USERS:
        print_error(
            f"User '{username}' already exists with phone {USERS[username]}. "
            f"Use 'change {username} <new_phone>' to update, or use a different username."
        )
        return

    USERS[username] = phone
    return f"{IDENT}{BOT_COLOR}Contact added.{Style.RESET_ALL}"


@input_error
def update_contact(args):
    """
    Update an existing contact's phone number.

    Args:
        args: List of [username, new_phone]. Must contain exactly 2 items.

    Returns:
        str: Formatted success message.

    Raises:
        ValueError: If args count != 2 or phone format is invalid.
        KeyError: If the username does not exist in USERS.
    """
    if len(args) != 2:
        raise ValueError(ERR_NAME_AND_PHONE)
    name, phone = args

    username = name.capitalize()

    validate_phone(phone)

    if username not in USERS:
        raise KeyError(f"User '{username}' doesn't exist.")

    USERS[username] = phone
    return f"{IDENT}{BOT_COLOR}Contact updated.{Style.RESET_ALL}"


@input_error
def get_users_phone(args: list):
    """
    Retrieve the phone number for a given username.

    Args:
        args: List where args[0] is the username to look up.

    Returns:
        str: Formatted message with the user's phone number.

    Raises:
        IndexError: If args is empty (no username provided).
        KeyError: If the username does not exist in USERS.
    """
    if not args:
        raise IndexError("Enter user name.")
    username = args[0].capitalize()

    if username not in USERS:
        raise KeyError(f"User '{username}' doesn't exist.")

    return f"{IDENT}{BOT_COLOR}{username}'s phone is {USERS[username]}{Style.RESET_ALL}"


def main():
    """
    Main application loop for the contact management bot.

    Handles user input, routes commands, and provides interactive feedback.
    """
    print(f"{BOT_COLOR}Welcome to the assistant bot!{Style.RESET_ALL}")

    # Command dictionary for cleaner routing
    commands = {
        "hello": lambda args: print_success("How can I help you?"),
        "add": add_contact,
        "change": update_contact,
        "phone": get_users_phone,
        "all": lambda args: print_dict_as_list(USERS, ["User", "Phone"]),
        "help": lambda args: print_dict_as_list(COMMANDS_HELP_INFO, ["Command", "Usage"]),
    }

    while True:
        user_input = input("Enter a command: ").strip()
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print(f"{BOT_COLOR}Good bye!{Style.RESET_ALL}")
            break
        elif command in commands:
            result = commands[command](args)
            if result:
                print(result)
        elif command:  # Only show error if command was entered and it's invalid
            print_error("Invalid command. Please use one of the list below:")
            print_dict_as_list(COMMANDS_HELP_INFO, ["Command", "Usage"])


if __name__ == "__main__":
    main()
