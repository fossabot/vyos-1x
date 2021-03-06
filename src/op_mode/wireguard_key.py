#!/usr/bin/env python3
#
# Copyright (C) 2018 VyOS maintainers and contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 or later as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import argparse
import os
import sys
import syslog as sl
import subprocess

from vyos import ConfigError

dir = r'/config/auth/wireguard'
pk  = dir + '/private.key'
pub = dir + '/public.key'

### check_kmod may be removed in the future, 
### once it's loaded automatically 
def check_kmod():
  if not os.path.exists('/sys/module/wireguard'):
    sl.syslog(sl.LOG_NOTICE, "loading wirguard kmod") 
    if  os.system('sudo modprobe wireguard') != 0:
      sl.syslog(sl.LOG_ERR, "modprobe wireguard failed")
      raise ConfigError("modprobe wireguard failed")

def generate_keypair():
  ret = subprocess.call(['wg genkey | tee ' + pk + '|wg pubkey > ' + pub], shell=True)
  if ret != 0:
    raise ConfigError("wireguard key-pair generation failed")
  else:
    sl.syslog(sl.LOG_NOTICE, "new keypair wireguard key generated in " + dir)

def genkey():
  ### if umask 077 makes trouble, 027 will work
  old_umask = os.umask(0o077)
  if os.path.exists(pk) and os.path.exists(pub):
    choice = input("You have a wireguard key-pair already, do you want to re-generate? [y/n] ")
    if choice == 'y' or choice == 'Y':
      generate_keypair()
  else:
    os.mkdir(dir)
    generate_keypair()
  os.umask(old_umask)

def showkey(key):
  if key == "pub":
    if os.path.exists(pub):
      print ( open(pub).read().strip() )
    else:
      print("no public key found")

  if key == "pk":
    if os.path.exists(pk):
      print ( open(pk).read().strip() )
    else:
      print("no private key found")

if __name__ == '__main__':
  check_kmod()

  parser = argparse.ArgumentParser(description='wireguard key management')
  parser.add_argument('--genkey', action="store_true", help='generate key-pair')
  parser.add_argument('--showpub', action="store_true", help='shows public key')
  parser.add_argument('--showpriv', action="store_true", help='shows private key')
  args = parser.parse_args()

  try:
    if args.genkey:
      genkey()
    if args.showpub:
      showkey("pub")
    if args.showpriv:
      showkey("pk")

  except ConfigError as e:
    print(e)
    sys.exit(1)

