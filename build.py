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
TELEMETRY_DIR = '/catapult/telemetry/'
sys.path.insert(1, TELEMETRY_DIR)
from telemetry.core import util
_MIN_GO_VERSION = [1, 23]
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
  if os_arch == 'x86_64' or os_arch == 'AMD64':
    os_arch = 'amd64'
  if os_arch == 'aarch64':
    os_arch = 'arm64'
  # go build command recognizes 'darwin' but not 'mac'.
  if os_name == 'mac':
    os_name = 'darwin'
  check_go_version()
  go_path_dir = None
  try:
    go_path_dir = tempfile.mkdtemp()
    env = os.environ.copy()
    env['GOPATH'] = go_path_dir
    env['GOOS'] = os_name
    env['GOARCH'] = os_arch
    env['CGO_ENABLED'] = '0'
    build_cmd = ['go', 'build', '-v', '-o', binary_name, '%s.go' % binary_name]
    print('Running build command: %s' % ' '.join(build_cmd))
    process = subprocess.Popen(build_cmd, env=env, cwd=_WPR_GO_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print("ERROR: Go build failed.")
        print("Standard Output:\n", stdout.decode())
        print("Standard Error:\n", stderr.decode())
        raise subprocess.CalledProcessError(process.returncode, build_cmd)

    out_dir = '/output/build/%s/%s' % (os_name, os_arch)
    os.makedirs(out_dir, exist_ok=True)
    shutil.move(os.path.join(_WPR_GO_DIR, binary_name), os.path.join(out_dir, binary_name))
  finally:
    if go_path_dir:
      shutil.rmtree(go_path_dir)
_SUPPORTED_PLATFORMS = (
  ('linux', 'x86_64'),
  ('linux', 'aarch64'),
  ('mac', 'arm64'),
)
def BuildAndUpdateGoBinary(binary_name, os_name, arch_name):
  if (os_name, arch_name) not in _SUPPORTED_PLATFORMS:
    raise NotImplementedError('OS = %s, ARCH = %s is not supported' %
        (os_name, arch_name))
  print('Build %s binary for OS %s, ARCH: %s' % (binary_name, os_name, arch_name))
  build_go_binary(binary_name, os_name, arch_name)

def main():
  for os_name, arch_name in _SUPPORTED_PLATFORMS:
    BuildAndUpdateGoBinary('wpr', os_name, arch_name)
  # The binary fills in placeholders in this script, so use both from the same commit.
  shutil.copy(os.path.join(_WPR_GO_DIR, '..', 'deterministic.js'), '/output/build/deterministic.js')
  subprocess.check_call(['go', 'clean', '-modcache'], cwd=_WPR_GO_DIR)

if __name__ == "__main__":
  sys.exit(main())
