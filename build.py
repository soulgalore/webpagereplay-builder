#!/usr/bin/env python3
# Copyright (c) 2017 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import os
import re
import shutil
import sys
import subprocess
import tempfile
import platform
TELEMETRY_DIR = '/catapult/telemetry/' #os.path.join(os.path.abspath(os.path.dirname(__file__)), 'telemetry')
sys.path.insert(1, TELEMETRY_DIR)
from telemetry.core import util
from telemetry.core import platform as platform_module
from telemetry.internal.util import binary_manager
import py_utils
# from telemetry.core import util
# rom telemetry.core import platform as platform_module
_MIN_GO_VERSION = [1, 12]
_WPR_GO_DIR = os.path.join(util.GetCatapultDir(), 'web_page_replay_go', 'src')
def check_go_version():
  try:
    out = subprocess.check_output(['go', 'version']).decode()
  except subprocess.CalledProcessError:
    out = 'no go binary found'
  match = re.findall(r'go(\d+).(\d+)', out)
  assert len(match) > 0, ('Unable to parse go version from "%s"' % out)
  version = [int(match[0][0]), int(match[0][1])]
  assert (version[0] > _MIN_GO_VERSION[0] or
    (version[0] == _MIN_GO_VERSION[0] and version[1] >= _MIN_GO_VERSION[1])), (
    'Require go version %s or higher. Found: %s' % (_MIN_GO_VERSION, version))
def build_go_binary(binary_name, os_name, os_arch):
  """ Build and return path to wpr go binary."""
  # go build command recognizes 'amd64' but not 'x86_64', so we switch 'x86_64'
  # to 'amd64' string here.
  # The two names can be used interchangbly, see:
  # https://wiki.debian.org/DebianAMD64Faq?action=recall&rev=65
  if os_arch == 'x86_64' or os_arch == 'AMD64':
    os_arch = 'amd64'
  if os_arch == 'x86':
    os_arch = '386'
  if os_arch == 'armv7l':
    os_arch = 'arm'
  if os_arch == 'aarch64':
    os_arch = 'arm64'
  if os_arch == 'mips':
    os_arch = 'mipsle'
  # go build command recognizes 'darwin' but not 'mac'.
  if os_name == 'mac':
    os_name = 'darwin'
  if os_name == 'win':
    os_name = 'windows'
  check_go_version()
  try:
    # We want to build wpr go binaries from the local source. We do this by
    # making a temporary GOPATH that symlinks to our local directory.
    go_path_dir = tempfile.mkdtemp()
    repo_dir = os.path.join(go_path_dir, 'src/github.com/catapult-project')
    os.makedirs(repo_dir)
    os.symlink(util.GetCatapultDir(), os.path.join(repo_dir, 'catapult'))
    env = os.environ.copy()
    env['GOPATH'] = go_path_dir
    env['GOOS'] = os_name
    env['GOARCH'] = os_arch
    env['CGO_ENABLED'] = '0'
    print('GOPATH=%s' % go_path_dir)
    print('CWD=%s' % _WPR_GO_DIR)
    get_cmd = ['go', 'get', '-d', './...']
    print('Running get command: %s' % ' '.join(get_cmd))
    subprocess.check_call(get_cmd, env=env, cwd=_WPR_GO_DIR)
    build_cmd = ['go', 'build', '-v', '%s.go' % binary_name]
    print('Running build command: %s' % ' '.join(build_cmd))
    process = subprocess.Popen(build_cmd, env=env, cwd=_WPR_GO_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print("ERROR: Go build failed.")
        print("Standard Output:\n", stdout.decode())
        print("Standard Error:\n", stderr.decode())
        raise subprocess.CalledProcessError(process.returncode, build_cmd)

    mkdir_cmd = ['mkdir', '-p', '/output/build/%s/%s' % (os_name,  os_arch)]
    subprocess.check_call(mkdir_cmd, env=env, cwd=_WPR_GO_DIR)
    mv_cmd = ['mv', 'wpr', '/output/build/%s/%s' % (os_name,  os_arch)]
    subprocess.check_call(mv_cmd, env=env, cwd=_WPR_GO_DIR)  
    clean_cmd = ['go', 'clean', '-modcache']
    print('Running clean command: %s' % ' '.join(clean_cmd))
    subprocess.check_call(clean_cmd, env=env, cwd=_WPR_GO_DIR)
  finally:
    if go_path_dir:
      shutil.rmtree(go_path_dir)
  if os_name == 'windows':
    return os.path.join(_WPR_GO_DIR, '%s.exe' % binary_name)
  return os.path.join(_WPR_GO_DIR, binary_name)
# TODO(nedn): support building other architectures & OSes.
_SUPPORTED_PLATFORMS = (
  #('win', 'x86'),
  #('mac', 'arm64'),
  #('mac', 'x86_64'),
  ('linux', 'x86_64'),
  #('win', 'AMD64'),
  #('linux', 'armv7l'),
  #('linux', 'aarch64')
)
def get_latest_wpr_go_commit_hash():
  return subprocess.check_output(
      ['git', 'log', '-n', '1', '--pretty=format:%H', _WPR_GO_DIR],
      text=True).strip()
def BuildAndUpdateGoBinary(binary_name, os_name, arch_name):
  if (os_name, arch_name) not in _SUPPORTED_PLATFORMS:
    raise NotImplementedError('OS = %s, ARCH = %s is not supported' %
        (os_name, arch_name))
  print('Build %s binary for OS %s, ARCH: %s' % (
      binary_name, os_name, arch_name))
  build_go_binary(binary_name, 'linux', 'x86_64')
  build_go_binary(binary_name, 'linux', 'armv7l')
  build_go_binary(binary_name, 'linux', 'aarch64')
  build_go_binary(binary_name, 'mac', 'x86_64')
  build_go_binary(binary_name, 'mac', 'arm64')

def main():
  for os_name, arch_name in _SUPPORTED_PLATFORMS:
    # wpr is the wpr binary for recording and replaying network traffic to allow
    # for consistent and hermetic tests.
    BuildAndUpdateGoBinary('wpr', os_name, arch_name)
    # httparchive is the wpr binary for interrogating and editing a wpr archive
    # that was previously recorded.
    # BuildAndUpdateGoBinary('httparchive', os_name, arch_name)
if __name__ == "__main__":
  sys.exit(main())