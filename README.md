# VaultBrowser

A terminal-based HashiCorp's Vault client

For the moment only supports generic/kv/kv2 secret backends.

![Screenhost](screenshot.png?raw=true "Screenhost")

## Installation
First install cdtui library: https://github.com/Carlos-Descalzi/cdtui
Install it from sources, there is no package available.

    sudo python3 setup.py install 
    or, for user setup:
    python3 setup.py install --prefix=$HOME/.local

## Configuration
In $HOME/.vaultbrowser two files are automatically generated:

**vaultbrowser.ini**: Basic configuration
* editor: Path to external editor program
* highlighter: External command used for json syntax highlighting, optional.

**services.ini**: List of vault instances to connect.

## Keys
* tab: cycle focus through pieces of the UI
* shift tab: same thing but in the opposite direction
* a: Add a new entry
* e: Edit a selected entry
* d: Delete selected entry
* h: Shows help.
* ESC: Closes any open popup, if none, closes the application.
