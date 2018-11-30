#!/usr/bin/env python
import os
import re
import sys
import ffmpeg
from glob import glob

DEBUG = False

def get_filename(bangumi_name, ep_name):
    return bangumi_name + '-' + ep_name + '.flv'

def concat_video(infiles, outfile):
    """
        concat infiles to one single outfile
    """
    ffmpeg.concat(*(ffmpeg.input(infile) for infile in infiles)) \
        .output(outfile) \
        .global_args('-loglevel', 'panic' if not DEBUG else 'quiet') \
        .run()

def tailname(path):
    if os.path.split(path)[1] != '':
        return os.path.split(path)[1]
    else:
        return os.path.basename(os.path.dirname(path))

def guess_bangumi_name(working_dir):
    """
        guess bilibili bangumi name
    """
    ini = os.path.join(working_dir, 'desktop.ini')
    content = open(ini, 'r', 10, "gb2312").read()
    match = re.search(r'InfoTip=(.*)', content)
    if match:
        return match.group(1)
    else:
        return None

def guess_ep_name(ep_dir):
    return os.path.basename(os.path.dirname(ep_dir))

def work(working_dir):
    bangumi_name = guess_bangumi_name(working_dir) or tailname(working_dir)
    print("[+] Start scan eps of {}.".format(bangumi_name))
    ep_dirs = glob(os.path.join(working_dir, '*/'))
    for ep_dir in ep_dirs:
        ep_name = tailname(ep_dir)
        filename = get_filename(bangumi_name, ep_name)
        part_paths = glob(os.path.join(ep_dir, '*.flv'))
        part_paths = sorted(part_paths) # will be wrong when len(parts) >= 10
        print("[+] Start concat parts in ep {}.\n[+] Output filename: {}.".format(ep_name, filename))
        print("[+] Concating... (it may be slow)")
        try:
            concat_video(part_paths, filename)
        except ffmpeg._run.Error:
            print("[-] Error! (see stderr output for detail)")
        print("[+] Finish.")

def main():
    if len(sys.argv) >= 2 and sys.argv[1]:
        bangumi_dir = sys.argv[1]
        work(bangumi_dir)
    else:
        print("Usage: {} <bangumi_dir>".format(sys.argv[0]))

if __name__ == "__main__":
    main()