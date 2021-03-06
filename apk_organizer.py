#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2015-05-21

@author: wanglei02
"""

import datetime
import locale
import os
import shutil
from distutils.dir_util import copy_tree

CHARSET_UTF8 = 'utf-8'
CHARSET_CURRENT = locale.getpreferredencoding()


def make_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)


def convert_encoding(s, original, convert_to):
    if original == convert_to:
        return s
    else:
        return s.decode(original).encode(convert_to)


# this is a generator
def list_files(d, file_filter=None, ignore=()):
    for x in os.listdir(d):
        full_dir = os.path.join(d, x)
        if os.path.isdir(full_dir):
            if not x in ignore:
                for y in list_files(full_dir, file_filter, ignore):
                    yield y
        else:
            if file_filter is None or file_filter(x):
                yield full_dir


def find_dir(d, name):
    for dirpath, dirnames, filenames in os.walk(d):
        if name in dirnames:
            return os.path.join(dirpath, name)


def find_file(d, name):
    for dirpath, dirnames, filenames in os.walk(d):
        if name in filenames:
            return os.path.join(dirpath, name)


def read_config():
    config_dict = {}
    config_file_path = os.path.join(os.path.curdir, 'config.txt')
    with open(convert_encoding(config_file_path, CHARSET_UTF8, CHARSET_CURRENT), 'r') as f:
        for line in f.readlines():
            stripped_line = line.strip()
            # line starts with '#' is a comment line
            if not stripped_line.startswith('#'):
                config_array = [s.strip() for s in stripped_line.split('=')]
                if len(config_array) == 2:
                    config_dict[config_array[0]] = config_array[1]
    android_project_path = config_dict.get('android_project_path')
    print 'From: %s' % android_project_path
    destination_path = config_dict.get('destination_path')
    print 'To: %s' % destination_path
    return android_project_path, destination_path


def is_release_apk(n):
    n_arr = os.path.splitext(n)
    return n_arr[1] == '.apk' and not n_arr[0].endswith('debug') and not n_arr[0].endswith('unaligned')


def copy_apk_files(src, dst):
    print 'Start'
    # current datetime to be the name of the folder
    date = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
    dst_base = os.path.join(convert_encoding(dst, CHARSET_UTF8, CHARSET_CURRENT), date)
    make_dir(dst_base)
    src_base = convert_encoding(src, CHARSET_UTF8, CHARSET_CURRENT)

    for src_apk in list_files(src_base, is_release_apk, ('bin',)):
        apk_name = os.path.split(src_apk)[1]
        dst_apk = os.path.join(dst_base, apk_name)
        shutil.copyfile(src_apk, dst_apk)
        print 'Copy %s to %s' % (convert_encoding(src_apk, CHARSET_CURRENT, CHARSET_UTF8),
                                 convert_encoding(dst_apk, CHARSET_CURRENT, CHARSET_UTF8))

    # 目录中包含build.gradle文件的为Android Studio的project，否则为Eclipse的project
    if find_file(src_base, 'build.gradle'):
        # Android Studio
        mapping_dirname = 'mapping'
    else:
        # Eclipse
        mapping_dirname = 'proguard'

    src_mapping = find_dir(src_base, mapping_dirname)
    if src_mapping:
        dst_mapping = os.path.join(dst_base, mapping_dirname)
        copy_tree(src_mapping, dst_mapping)
        print 'Copy %s into %s' % (convert_encoding(src_mapping, CHARSET_CURRENT, CHARSET_UTF8),
                                   convert_encoding(dst_mapping, CHARSET_CURRENT, CHARSET_UTF8))

    print 'Done'


if __name__ == '__main__':
    src, dst = read_config()
    copy_apk_files(src, dst)
