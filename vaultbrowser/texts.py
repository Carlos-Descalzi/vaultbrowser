from .util import ansi

HELP=f"""
{ansi.BOLD}HELP{ansi.RESET}
{ansi.BOLD}===={ansi.RESET}

Keyboard:
    {ansi.BOLD}Ctrl-h:{ansi.RESET} Shows this help window.
    {ansi.BOLD}Ctrl-a:{ansi.RESET} Add a new entry
    {ansi.BOLD}Ctrl-e:{ansi.RESET} Edit current entry
    {ansi.BOLD}Ctrl-d:{ansi.RESET} Remove current entry
    {ansi.BOLD}Enter:{ansi.RESET}  Select item on focused view.
    {ansi.BOLD}Tab:{ansi.RESET}    Cycle focus across views.
    {ansi.BOLD}Esc:{ansi.RESET}    Closes popups if any open, otherwise exits application.
"""
