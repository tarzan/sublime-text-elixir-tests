Sublime Text Elixir Tests
=========================

Overview
--------

A sublime-2 testrunner for Elixir.

Forked from:

https://github.com/tarzan/sublime-text-elixir-tests

https://github.com/maltize/sublime-text-2-ruby-tests

Some stuff is broken! Gladly accepting pull-requests to fix bugs or restore functionality.


Roadmap
------------
Considering working on a re-write in the future forked directly from RubyTest.

Installation
------------

Go to your Sublime Text `Packages` directory

 - OS X: `~/Library/Application\ Support/Sublime\ Text\ 2/Packages`
 - Windows: `%APPDATA%/Sublime Text 2/Packages/`
 - Linux: `~/.config/sublime-text-2/Packages/`

and clone the repository using the command below:

``` shell
git clone https://github.com/molenick/sublime-text-elixir-tests.git ElixirTest
```

Settings
--------

'Sublime Text' -> 'Preferences' -> 'Package Settings' -> 'ElixirTest'

Make a copy of `ElixirTest.sublime-settings` file to `~/Library/Application\ Support/Sublime\ Text\ 2/Packages/User/` and make your changes.

For Linux, the path is `:~/.config/sublime-text-3/Packages/User/`.

Usage
-----

 - Run single elixir test: `Command-Shift-R`
 - Run all elixir tests from current file: `Command-Shift-T`
 - Run last elixir test(s): `Command-Shift-E`
 - Show test panel: `Command-Shift-X` (when test panel visible hit `esc` to hide it)
 - Switching between code and test:
    - Single View: `Command-.`
    - Split View:  `Command-Ctrl-.`


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

      "theme": "Packages/ElixirTest/Console.hidden-tmTheme",
      "syntax": "Packages/ElixirTest/TestConsole.tmLanguage",

      "terminal_encoding": "utf-8"
    }
