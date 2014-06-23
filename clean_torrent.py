# -*- coding: UTF-8 -*-
import os
import bencode
import random
import string
from bencode import BTFailure

video_ext = ['.avi', '.rmvb', '.rm', '.asf', '.divx', '.mpg', '.mpeg', '.mpe', '.wmv', '.mp4', '.mkv', '.vob']
key_str = ['#', '@', '_', '-',
           'sexinsex', 'sis', 'sex8', '6ytk',
           '第一会所','第一會所', '草榴', '色中色', '六月天空',
           '加勒比', '1pondo', '一本道', '東京熱', 'tokyo hot',
           '中文字幕', '中出', '自拍', '无码', '国产']


def filter(content):
    for key in key_str:
        content = content.lower().replace(key, '')

    return content


def trash_useless(data):  # dump useless info
    keys = [
        'publisher-url',
        'publisher',
        'publisher-url.utf-8',
        'publisher.utf-8']
        # 'name.utf-8',]
    for k in keys:
        if k in data['info']:
            data['info'].pop(k)
    if 'comment' in data:
        data.pop('comment')
    return data


def single_file(info):
    # ext = path.splitext(info['name'])[1]
    info['name'] = filter(info['name'])
    return info


def strB2Q(ustring):

    rstring = u""
    for uchar in ustring:

        inside_code=ord(uchar)
        if inside_code == 32:                                 #半角空格直接转化
            inside_code = 12288
        elif 32 <= inside_code <= 126:        #半角字符（除空格）根据关系转化
            inside_code += 65248

        rstring += unichr(inside_code)
    return rstring


def multi_file(info):

    if info.get('name.utf-8'):
        info['name.utf-8'] = strB2Q(info['name.utf-8'].decode('utf-8', 'ignore')).encode('utf-8')

    info['name'] = filter(info['name'])

    for i in info['files']:
        if 'path.utf-8' in i:
            i.pop('path.utf-8')

        if 'path' in i:
            name = os.path.splitext(i['path'][0])[0]
            ext = os.path.splitext(i['path'][0])[1].lower()

            if not ext in video_ext:
                i['path'] = [""]
            else:
                i['path'][0] = ''.join(random.sample(string.ascii_letters+string.digits, 8)) + ext

    return info


def clean(torrent):

    try:
        decoded_data = bencode.bdecode(torrent)
        old_info = decoded_data['info']
    except BTFailure:
        print "error, not a valid torrent."
    else:

        if 'files' in old_info:
            decoded_data['info'] = multi_file(old_info)
        else:
            decoded_data['info'] = single_file(old_info)

        return bencode.bencode(trash_useless(decoded_data))


def clean_folder(folder, dest_folder):

    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)

    for file_name in os.listdir(folder):

        path = os.path.join(folder, file_name)
        dest_path = os.path.join(dest_folder, file_name)

        if os.path.isdir(path):
            clean_folder(path, dest_path)

        if os.path.exists(dest_path) or os.path.splitext(file_name)[1].lower() != '.torrent':
            continue

        try:
            with open(path, 'rb') as t:
                with open(dest_path, 'wb') as dest_torrent:
                    dest_torrent.write(clean(t.read()))

        except Exception, e:
            print e


if __name__ == "__main__":
    clean_folder(os.sys.argv[1] or '.\\', '.\\seed')
