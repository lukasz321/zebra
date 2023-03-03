import time
import sys
import re
from termios import tcflush, TCIFLUSH
from typing import List, Tuple
from dateutil.relativedelta import relativedelta, MO
from datetime import date

from .utils import get_operator
from . import log


class Prompt:
    """
    Class helping operators interact with shell.
    Ask for input, ask for acknowledgement, prompt yes or no.

    Heavily influenced by click module.
    See __main__ at the bottom of this file for examples.
    """

    CYAN = "\033[96m\033[1m"
    YLW = "\033[93m\033[1m"
    GRAY = "\033[0m\033[1m"
    ENDC = "\033[0m\033[0m"

    @staticmethod
    def date_range() -> Tuple[str, str]:
        """
        Ask user start and end date.
        Use case: asking for records generated between date YYYY-MM-DD and YYYY2-MM2-DD2.

        Returns
        -------
            Tuple(str(start_date), str(end_date)
        """

        while True:
            print("""\nValid options:
    * w -- since Monday
    * t -- today
    * m -- 30 days ago
    """
            )
            start_date = Prompt.input("ENTER START DATE")
            if start_date == "w":
                today = date.today()
                last_monday = today + relativedelta(weekday=MO(-1))
                start_date = last_monday.strftime("%Y-%m-%d")
                break

            if start_date == "t":
                today = date.today()
                start_date = today.strftime("%Y-%m-%d")
                break
            
            if start_date == "m":
                today = date.today()
                mo = today - relativedelta(days=30)
                start_date = mo.strftime("%Y-%m-%d")
                break

            p = re.compile("\d{4}-\d{2}-\d{2}")
            if p.match(start_date):
                break

            print(Prompt.YLW + "Nope! Expecting YYYY-MM-DD." + Prompt.ENDC + "\n")

        while True:
            print("""\nValid options:
    * w -- since Monday
    * t -- today
    * m -- 30 days ago
    """
            )
            end_date = Prompt.input("ENTER END DATE")
            if end_date == "w":
                today = date.today()
                last_monday = today + relativedelta(weekday=MO(-1))
                end_date = last_monday.strftime("%Y-%m-%d")
                break

            if end_date == "t":
                today = date.today()
                end_date = today.strftime("%Y-%m-%d")
                break
            
            if end_date == "m":
                today = date.today()
                mo = today - relativedelta(days=30)
                end_date = mo.strftime("%Y-%m-%d")
                break

            p = re.compile("\d{4}-\d{2}-\d{2}")
            if p.match(end_date):
                break

            print(Prompt.YLW + "Nope! Expecting YYYY-MM-DD." + Prompt.ENDC + "\n")

        return (start_date, end_date)

    @staticmethod
    def choose(prompt: str, options: List) -> str:
        """
        Ask user for input. Input is limited to the options provided
        as an argument. User must choose one of the options.

        Note that options are case sensitive.

        Returns
        -------
            user_input: str - one of the options provided as an arg
                              most likely a string/int
        """

        if prompt[-1:] not in [":", "?", ".", "!"]:
            prompt = prompt + ":"

        while True:
            print("")
            log.info(f"Valid (case sensitive) options are: {options}", bold=True)
            user_input = input(f">> {Prompt.CYAN}{prompt}{Prompt.ENDC} ")
            if user_input in options:
                return user_input

            log.error(f'"{user_input}" is not a valid option!')

    @staticmethod
    def confirm(prompt: str):
        """
        An alias for Prompt.acknowledge.
        """

        Prompt.acknowledge(prompt=prompt)

    @staticmethod
    def acknowledge(prompt: str):
        """
        Prompt user to hit ENTER.
        """

        if prompt[-1:] not in [":", "?", ".", "!"]:
            prompt = prompt + "."

        operator = get_operator()

        while True:
            tcflush(sys.stdin, TCIFLUSH)
            if operator:
                inp = input(f">> {Prompt.CYAN}{prompt}{Prompt.ENDC} "\
                        f"{operator.title()}, please type \"I understood\": ")
            else:
                inp = input(f">> {Prompt.CYAN}{prompt}{Prompt.ENDC} Type \"I understood\": ")
            if "i understood" in inp.lower():
                break

    @staticmethod
    def wait(seconds: int, prompt: str = "Retrying in"):
        """
        Essentially a nice "interactive" sleep time with a countdown.
        """

        print("")
        for i in range(1, seconds + 1):
            log.info(
                f"{prompt} {seconds-i} seconds...",
                fg="white",
                inline=True,
            )
            time.sleep(1)

    @staticmethod
    def input(prompt: str, flush: bool = False) -> str:
        """
        Ask operator for input. Note that no input is accepted.

        Returns
        -------
            str: user_input - may be empty.
        """

        if flush:
            tcflush(sys.stdin, TCIFLUSH)

        user_input = input(f">> {Prompt.CYAN}{prompt}{Prompt.ENDC}: ")
        return user_input

    @staticmethod
    def yes_no(prompt: str) -> bool:
        """
        Ask operator to choose "y" or "n" to prompt.

        Returns
        -------
            bool: True  - if operator chose "y"
            bool: False - if operator chose "n"
        """

        if prompt.endswith(":") or prompt.endswith("."):
            prompt = prompt[:-1]

        while True:
            user_input = input(
                f">> {Prompt.CYAN}{prompt} {Prompt.GRAY}[Y/n]{Prompt.ENDC}: "
            )
            if user_input:
                if user_input.lower() == "y":
                    return True
                if user_input.lower() == "n":
                    return False

            log.error(f'"{user_input}" is an invalid input! Enter "y" or "n".')


if __name__ == "__main__":
    Prompt.acknowledge("Restart the terminal.")
    print(Prompt.date_range())
    true_or_false = Prompt.yes_no("Works?")
    user_input = Prompt.input("How old are you?")
    true_or_false = Prompt.confirm("Press ENTER if you accept the terms")
    Prompt.confirm("Do you confirm?")
    user_choice = Prompt.choose(
        "Choose [A] if you like apples or [P] if you like pears", options=["a", "p"]
    )
