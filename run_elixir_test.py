import os
import re
import functools
import sublime
import string
import sublime_plugin

class ShowInPanel:
  def __init__(self, window):
    self.window = window

  def display_results(self):
    self.panel = self.window.get_output_panel("exec")
    self.window.run_command("show_panel", {"panel": "output.exec"})
    self.panel.settings().set("color_scheme", THEME)
    self.panel.set_syntax_file(SYNTAX)
    if HIDE_PANEL:
      self.window.run_command("hide_panel")
    self.panel.settings().set("color_scheme", THEME)


class ShowInScratch:
  def __init__(self, window):
    self.window = window
    self.active_for = 0
    self.copied_until = 0

  def display_results(self):
    self.panel = self.window.get_output_panel("exec")
    self.window.run_command("hide_panel")
    self.view = self.window.open_file("Test Results")
    self.view.set_scratch(True)
    self.view.set_read_only(False)

    self.view.set_syntax_file(SYNTAX)
    self.view.settings().set("color_scheme", THEME)
    self.view.set_read_only(True)
    self.poll_copy()
    self.append('\n\n')

  def poll_copy(self):
    # FIXME HACK: Stop polling after one minute
    if self.active_for < 60000:
      self.active_for += 50
      sublime.set_timeout(self.copy_stuff, 50)

  def append(self, content):
    self.view.set_read_only(False)
    edit = self.view.begin_edit()
    self.view.insert(edit, self.view.size(), content)
    self.view.end_edit(edit)
    self.view.set_read_only(True)
    self.view.set_viewport_position((self.view.size(), self.view.size()), True)

  def copy_stuff(self):
    size = self.panel.size()
    content = self.panel.substr(sublime.Region(self.copied_until, size))
    if content:
      self.copied_until = size
      self.append(content)
    self.poll_copy()


class ShowPanels:
  def __init__(self, window):
    self.window = window

  def split(self):
    self.window.run_command('set_layout', {
                          "cols": [0.0, 0.5, 1.0],
                          "rows": [0.0, 1.0],
                          "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
                      })
    self.window.focus_group(1)


class ElixirTestSettings:
  def __init__(self):
    self.settings = sublime.load_settings("ElixirTest.sublime-settings")

  def __getattr__(self, name):
    if not self.settings.has(name):
      raise AttributeError(name)
    value = sublime.active_window().active_view().settings().get(name)
    if value:
      return lambda **kwargs: value.format(**kwargs)
    return lambda **kwargs: self.settings.get(name).format(**kwargs)


class BaseMixTask(sublime_plugin.TextCommand):
  def load_config(self):
    s = sublime.load_settings("ElixirTest.sublime-settings")
    global MIX_TEST_FOLDER; MIX_TEST_FOLDER = s.get("mix_test_folder")
    global IGNORED_DIRECTORIES; IGNORED_DIRECTORIES = s.get("ignored_directories")
    global HIDE_PANEL; HIDE_PANEL = s.get("hide_panel")
    global BEFORE_CALLBACK; BEFORE_CALLBACK = s.get("before_callback")
    global AFTER_CALLBACK; AFTER_CALLBACK = s.get("after_callback")
    global COMMAND_PREFIX; COMMAND_PREFIX = False
    global SAVE_ON_RUN; SAVE_ON_RUN = s.get("save_on_run")
    global SYNTAX; SYNTAX = s.get('syntax')
    global THEME; THEME = s.get('theme')
    global TERMINAL_ENCODING; TERMINAL_ENCODING = s.get('terminal_encoding')


    mix   = s.get("check_for_mix") #does nothing yet

  def save_all(self):
    if SAVE_ON_RUN:
      self.window().run_command("save_all")

  def is_executable(self, path):
    return os.path.isfile(path) and os.access(path, os.X_OK)

  def save_test_run(self, command, working_dir):
    s = sublime.load_settings("ElixirTest.last-run")
    s.set("last_test_run", command)
    s.set("last_test_working_dir", working_dir)

    sublime.save_settings("ElixirTest.last-run")

  def run_shell_command(self, command, working_dir):
    if not command:
      return False
    if BEFORE_CALLBACK:
      os.system(BEFORE_CALLBACK)
    if AFTER_CALLBACK:
      command += " ; " + AFTER_CALLBACK
    self.save_test_run(command, working_dir)
    if COMMAND_PREFIX:
      command = COMMAND_PREFIX + ' ' + command
    if int(sublime.version().split('.')[0]) <= 2:
      command = [command]
    self.view.window().run_command("exec", {
      "cmd": command,
      "shell": True,
      "working_dir": working_dir,
      "file_regex": r"([^ ]*\.ex?):?(\d*)",
      "encoding": TERMINAL_ENCODING
    })
    self.display_results()
    return True

  def display_results(self):
    display = ShowInScratch(self.window()) if USE_SCRATCH else ShowInPanel(self.window())
    display.display_results()

  def window(self):
    return self.view.window()

  class BaseFile(object):
    def __init__(self, file_name, partition_folder=""):
      self.folder_name, self.file_name = os.path.split(file_name)
      self.partition_folder = partition_folder
      self.absolute_path = file_name
    def parent_dir_name(self):
      head_dir, tail_dir = os.path.split(self.folder_name)
      return tail_dir
    def possible_alternate_files(self): return []
    def run_all_tests_command(self): return None
    def get_project_root(self): return self.folder_name
    def find_project_root(self):
      to_find = os.sep + self.partition_folder + os.sep
      project_root, _, _ = self.absolute_path.partition(to_find)
      return project_root
    def relative_file_path(self):
      to_find = os.sep + self.partition_folder + os.sep
      _, _, relative_path = self.absolute_path.partition(to_find)
      return self.partition_folder + os.sep + relative_path
    def get_current_line_number(self, view):
      char_under_cursor = view.sel()[0].a
      return view.rowcol(char_under_cursor)[0] + 1
    def features(self): return []

  class AnonymousFile(BaseFile):
    def __init__(self):
      True

  class ElixirFile(BaseFile):
    def possible_alternate_files(self): return [self.file_name.replace(".ex", "_test.exs"), self.file_name.replace(".exs", "_test.exs"), "test_" + self.file_name]
    def features(self): return ["switch_to_test"]

  class TestFile(ElixirFile):
    def possible_alternate_files(self): return list( set( [self.file_name.replace("_test.exs", ".ex"), self.file_name.replace("_test.exs", ".exs")] ) - set([self.file_name]) )
    def run_all_tests_command(self): return ElixirTestSettings().run_mix_command(relative_path=self.relative_file_path())
    def run_single_test_command(self, view): return ElixirTestSettings().run_single_mix_command(relative_path=self.relative_file_path(), line_number=self.get_current_line_number(view))
    def features(self): return super(BaseMixTask.TestFile, self).features() + ["run_test"]
    def get_project_root(self): return self.find_project_root()

  def find_partition_folder(self, file_name, default_partition_folder):
    folders = self.view.window().folders()
    file_name = file_name.replace("\\","\\\\")
    for folder in folders:
      folder = folder.replace("\\","\\\\")
      if re.search(folder, file_name):
        return re.sub(os.sep + '.+', "", file_name.replace(folder,"")[1:])
    return default_partition_folder

  def file_type(self, file_name = None, load_config = True):
    if load_config:
      self.load_config()
    file_name = file_name or self.view.file_name()
    if not file_name: return BaseMixTask.AnonymousFile()
    if re.search('\w+\_test.exs', file_name):
      partition_folder = self.find_partition_folder(file_name, MIX_TEST_FOLDER)
      return BaseMixTask.TestFile(file_name, partition_folder)
    elif re.search('\w+\.ex?', file_name):
      return BaseMixTask.ElixirFile(file_name)
    else:
      return BaseMixTask.BaseFile(file_name)


class RunSingleElixirTest(BaseMixTask):
  def is_enabled(self): return 'run_test' in self.file_type().features()
  def run(self, args):
    self.load_config()
    self.save_all()
    file = self.file_type()
    command = file.run_single_test_command(self.view)
    self.run_shell_command(command, file.get_project_root())


class RunAllElixirTest(BaseMixTask):
  def is_enabled(self): return 'run_test' in self.file_type().features()
  def run(self, args):
    self.load_config()
    self.save_all()
    file = self.file_type(self.view.file_name())
    command = file.run_all_tests_command()
    if self.run_shell_command(command, file.get_project_root()):
      pass
    else:
      sublime.error_message("Only *.exs files supported!")


class RunLastElixirTest(BaseMixTask):
  def load_last_run(self):
    self.load_config()
    self.save_all()
    s = sublime.load_settings("ElixirTest.last-run")
    return (s.get("last_test_run"), s.get("last_test_working_dir"))

  def run(self, args):
    last_command, working_dir = self.load_last_run()
    self.run_shell_command(last_command, working_dir)


class SwitchBetweenCodeAndTest(BaseMixTask):
  def is_enabled(self): return 'switch_to_test' in self.file_type().features()
  def run(self, args, split_view):
    self.load_config()
    possible_alternates = self.file_type().possible_alternate_files()
    alternates = self.project_files(lambda file: file in possible_alternates)

    for alternate in alternates:
      if re.search(self.file_type().parent_dir_name(), alternate):
        alternates = [alternate]
        break

    if alternates:
      if split_view:
        ShowPanels(self.window()).split()
      if len(alternates) == 1:
        self.window().open_file(alternates.pop())
      else:
        callback = functools.partial(self.on_selected, alternates)
        self.window().show_quick_panel(alternates, callback)
    else:
      GenerateTestFile(self.window(), split_view).doIt()

  def on_selected(self, alternates, index):
    if index == -1:
      return

    self.window().open_file(alternates[index])

  def walk(self, directory):
    for dir, dirnames, files in os.walk(directory):
      dirnames[:] = [dirname for dirname in dirnames if dirname not in IGNORED_DIRECTORIES]
      yield dir, dirnames, files

  def project_files(self, file_matcher):
    directories = self.window().folders()
    return [os.path.join(dirname, file) for directory in directories for dirname, _, files in self.walk(directory) for file in filter(file_matcher, files)]


class ShowTestPanel(BaseMixTask):
  def run(self, args):
    self.window().run_command("show_panel", {"panel": "output.exec"})


class GenerateTestFile:
  relative_paths = []
  full_torelative_paths = {}
  rel_path_start = 0

  def __init__(self, window, split_view):
    self.window = window
    self.split_view = split_view

  def doIt(self):
    self.build_relative_paths()
    self.window.show_quick_panel(self.relative_paths, self.dir_selected)

  def build_relative_paths(self):
      folders = self.active_project(self.window.folders())
      view = self.window.active_view()
      self.relative_paths = []
      self.full_torelative_paths = {}
      for path in folders:
          rootfolders = os.path.split(path)[-1]
          self.rel_path_start = len(os.path.split(path)[0]) + 1
          if self.is_valid_path(path):
            self.full_torelative_paths[rootfolders] = path
            self.relative_paths.append(rootfolders)

          for base, dirs, files in os.walk(path):
              for dir in dirs:
                  relative_path = os.path.join(base, dir)[self.rel_path_start:]
                  if self.is_valid_path(relative_path):
                    self.full_torelative_paths[relative_path] = os.path.join(base, dir)
                    self.relative_paths.append(relative_path)

  def active_project(self, folders):
    for folder in folders:
      project_name = os.path.split(folder)[-1]
      if re.search(project_name, self.current_file()):
        return [folder]
    return folders

  def is_valid_path(self, path):
    if re.search(self.test_path_re(), self.current_file()):
      return re.search('lib(\/|\\\)|(lib|extras)$', path) and not re.search('assets|views|vendor', path)
    else:
      return re.search(self.test_path_re(), path)

  def test_path_re(self):
    return MIX_TEST_FOLDER

  def current_file(self):
    return self.window.active_view().file_name()

  def dir_selected(self, selected_index):
      if selected_index != -1:
          self.selected_dir = self.relative_paths[selected_index]
          self.selected_dir = self.full_torelative_paths[self.selected_dir]
          self.window.show_input_panel("File name", self.suggest_file_name(self.selected_dir), self.file_name_input, None, None)

  def suggest_file_name(self, path):
    current_file = os.path.split(self.current_file())[-1]
    return self.set_file_name(path, current_file)

  def set_file_name(self, path, current_file):
    if re.search(self.test_path_re(), self.current_file()):
      return re.sub('_test.exs', '.ex', current_file)
    else:
      return current_file.replace('.ex', self.detect_test_type(path))

  def detect_test_type(self, path):
    if re.search(MIX_TEST_FOLDER, path):
      return '_test.exs'

  def file_name_input(self, file_name):
      full_path = os.path.join(self.selected_dir, file_name)

      if os.path.lexists(full_path):
          sublime.error_message('File already exists:\n%s' % full_path)
          return
      else:
          self.create_and_open_file(full_path)

  def create_and_open_file(self, path):
      if not os.path.exists(path):
          self.create(path)

      if self.split_view:
        ShowPanels(self.window).split()

      self.window.open_file(path)

  def create(self, filename):
      base, filename = os.path.split(filename)
      self.create_folder(base)

  def create_folder(self, base):
      if not os.path.exists(base):
          parent = os.path.split(base)[0]
          if not os.path.exists(parent):
              self.create_folder(parent)
          os.mkdir(base)


class GenerateFile(sublime_plugin.WindowCommand):
  def run(self):
    GenerateNewFile(self.window).doIt()


class GenerateNewFile(GenerateTestFile):
  def __init__(self, window):
    self.window = window
    self.split_view = False

  def active_project(self, folders):
    return folders

  def is_valid_path(self, path):
    return not re.search('\.\w+', path)

  def suggest_file_name(self, path):
    return ""
