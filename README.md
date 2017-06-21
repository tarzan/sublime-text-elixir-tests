Sublime Text Elixir Tests
=========================

Overview
--------
Running:

  - Elixir tests (all tests with mix: from file / single test)

Installation
------------

Go to your Sublime Text `Packages` directory

 - OS X: `~/Library/Application\ Support/Sublime\ Text\ 2/Packages`
 - Windows: `%APPDATA%/Sublime Text 2/Packages/`
 - Linux: `~/.config/sublime-text-2/Packages/`

and clone the repository using the command below:

``` shell
git clone https://github.com/tarzan/sublime-text-elixir-tests.git ElixirTest
```

Settings
--------

'Sublime Text' -> 'Preferences' -> 'Package Settings' -> 'ElixirTest'

Make a copy of `ElixirTest.sublime-settings` file to `~/Library/Application\ Support/Sublime\ Text\ 2/Packages/User/` and make your changes.


Usage
-----

 - Run single elixir test: `Command-Shift-R`
 - Run all elixir tests from current file: `Command-Shift-T`
 - Run last elixir test(s): `Command-Shift-E`
 - Show test panel: `Command-Shift-X` (when test panel visible hit `esc` to hide it)
 - Switching between code and test (create a file if not found):
    - Single View: `Command-.`
    - Split View:  `Command-Ctrl-.`
Keys:
 'Command' (OSX)
 'Ctrl' (Linux / Windows)

Settings:
---------

    {
      "run_mix_command": "mix {relative_path}",
      "run_single_mix_command": "mix {relative_path}:{line_number}",

      "mix_test_folder": "test",

      "check_for_mix": false,

      "save_on_run": false,
      "ignored_directories": [".git", "vendor", "tmp"],

      "hide_panel": false,

      "before_callback": "",
      "after_callback": "",

      "theme": "Packages/RubyTest/TestConsole.hidden-tmTheme",
      "syntax": "Packages/RubyTest/TestConsole.tmLanguage",

      "terminal_encoding": "utf-8"
    }
