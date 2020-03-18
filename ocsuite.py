"""Fully automated ordered chapters creation from a remuxed BDMV."""
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '18 March 2020'

import xml.etree.ElementTree as ET
from inspect import stack as n
from os import urandom
from random import choice, randint, sample
from sys import byteorder
from typing import Dict, List, Tuple, Union

import acsuite
import vapoursynth as vs

core = vs.core


# noinspection PyProtectedMember
def ordered_chapters(chapters: Dict[str, Tuple[int, int]],
                     /,
                     repeated_chapters: List[str],
                     remuxed_bdmv: str,
                     save_vs_clips_to_file: bool = False):
    """
    Creates ordered chapters .xml files, a simple VS script for splitting the BDMV into episode clips, and cuts audio.

    :param chapters: a dict of strings and frame ranges in the following format:
        chapters = {'ep_num|chap_name': (start_frame, end_frame), ...}
        where start_frame and end_frame are INCLUSIVE, different from normal Python slicing syntax.
        i.e.:
        chapters = {
            '01|Part A':      (0, 3770),
            '01|Title Card':  (3771, 3860),
            '01|Part B':      (3861, 20883),
            '01|Middle Card': (20884, 21003),
            '01|Part C':      (21004, 30041),
            '01|OP':          (30042, 32200),
            '01|Part D':      (32201, 33685),
            '01|Preview':     (33686, 34045),

            '02|Part A':      (34070, 35747),
            '02|OP':          (35748, 37906),
            '02|Part B':      (37907, 51308),
            '02|Middle Card': (51309, 51428),
            '02|Part C':      (51429, 65047),
            '02|ED':          (65048, 67180),
            '02|Part D':      (67181, 67732),
            '02|Preview':     (67733, 68092)
        }
        See tests.py for a full example.

    :param repeated_chapters: a list of chapters that will be encoded separately from the main episodes
        i.e. `['OP', 'ED']`
        these chapter names must appear at least once in the dict as a 'chap_name'

    :param remuxed_bdmv: `'/path/to/remuxed_bdmv.mkv'`
        Works best if *entire show is remuxed into a single, continuous stream* in a .mkv file.
        For more infomation on the commands needed to combine multiple volumes of a BDMV into a single .mkv file,
        see README.md.

    :param save_vs_clips_to_file: whether or not to print a simple VapourSynth script for cutting the BDMV into episode
                                  clips or to save it to a file, 'ordered_chapters_script.vpy'
    """

    suids = {i: _segment_uid_generator() for i in repeated_chapters}  # assigns a unique SUID to each repeated chapter

    # creates a tree of {'episode': {'chap1': (sframe, eframe), ...}}
    tree = {}  # Dict[str, Dict[str, Tuple[int, int]]]
    for ep_str, frames in chapters.items():
        ep_num, chap_name = ep_str.split('|')
        tree.setdefault(ep_num, {})[chap_name] = frames

    # creates a dict of {'episode': [sframe1, sframe2, ...]} not including repeated chapters
    # used for creating the VapourSynth clips and audio cutting
    begins, ends = {}, {}  # Dict[str, List[int]]
    for ep_num in tree:
        begins[ep_num], ends[ep_num]= [], []
        for chap_name in tree[ep_num]:
            if chap_name not in repeated_chapters:
                begins[ep_num].append(tree[ep_num][chap_name][0])
                ends[ep_num].append(tree[ep_num][chap_name][1])

    clip_list = {}  # Dict[str, Tuple[List[int], List[int]]]
    for ep_num in begins:
        combined = _combine(begins[ep_num], ends[ep_num])
        clip_list[ep_num] = combined  # combines lists for audio cutting + splicing
    for repeated_chap_name in repeated_chapters:
        for ep_num in tree:
            if repeated_chap_name in tree[ep_num]:
                clip_list[repeated_chap_name] = ([tree[ep_num][repeated_chap_name][0]], [tree[ep_num][repeated_chap_name][1]])
                break  # creates a clip for repeated chapters

    # prints clips and required SUIDs (or saves to file)
    if save_vs_clips_to_file:
        save_string = ['import vapoursynth as vs', 'core = vs.core', f'bdmv = core.lsmas.LWLibavSource(r\'{remuxed_bdmv}\')']
    else:
        print(f'import vapoursynth as vs\ncore = vs.core\nbdmv = core.lsmas.LWLibavSource(r\'{remuxed_bdmv}\')')

    for ep_num in clip_list:
        if ep_num in repeated_chapters:
            string = f'{ep_num}='
        else:
            string = f'ep{ep_num}='

        if save_vs_clips_to_file:
            if len(clip_list[ep_num][0]) == 1:  # for chapters with only one frame tuple
                if ep_num in repeated_chapters:
                    string += f'bdmv[{clip_list[ep_num][0][0]}:{clip_list[ep_num][1][0] + 1}]  # SUID: {suids[ep_num]}'
                else:
                    string += f'bdmv[{clip_list[ep_num][0][0]}:{clip_list[ep_num][1][0] + 1}]'
            else:
                for i in range(len(clip_list[ep_num][0])):
                    string += f'bdmv[{clip_list[ep_num][0][i]}:{clip_list[ep_num][1][i] + 1}]+'
                string = string[:-1]
            save_string.append(string)
        else:
            if len(clip_list[ep_num][0]) == 1:
                if ep_num in repeated_chapters:
                    print(string + f'bdmv[{clip_list[ep_num][0][0]}:{clip_list[ep_num][1][0] + 1}]  # SUID: {suids[ep_num]}')
                else:
                    print(string + f'bdmv[{clip_list[ep_num][0][0]}:{clip_list[ep_num][1][0] + 1}]')
            else:
                for i in range(len(clip_list[ep_num][0])):
                    string += f'bdmv[{clip_list[ep_num][0][i]}:{clip_list[ep_num][1][i] + 1}]+'
                print(string[:-1])

    if save_vs_clips_to_file:
        file = open('ordered_chapters_script.vpy', 'x')
        for i in save_string: file.write(i + '\n')
        file.close()
        print('VapourSynth and SUID information written to ordered_chapters_script.vpy')

    # creates a dict of {'episode': [(sframe1, eframe1), (sframe2, eframe2), ...]} for eztrim call
    call_list_trims = {}  # Dict[str, List[Tuple[int, int]]]
    for ep_num in clip_list:
        if len(clip_list[ep_num][0]) == 1:
            call_list_trims[ep_num] = (clip_list[ep_num][0][0], clip_list[ep_num][1][0] + 1)
        else:
            call_list_trims[ep_num] = []
            for f in range(len(clip_list[ep_num][0])):
                call_list_trims[ep_num].append((clip_list[ep_num][0][f], clip_list[ep_num][1][f] + 1))

    if '.mkv' in remuxed_bdmv:
        bdmv_clip = core.lsmas.LWLibavSource(remuxed_bdmv)
    else:
        bdmv_clip = core.std.BlankClip(fpsnum=24000, fpsden=1001)
        print('Using a fake test clip, no audio will be cut.')

    if '.mkv' in remuxed_bdmv:
        for ep_num in clip_list:
            acsuite.eztrim(bdmv_clip, call_list_trims[ep_num], audio_file=remuxed_bdmv, outfile=f'{ep_num}_cut_audio.wav')

    timestamps = {}  # Dict[str, Union[Tuple[str, str], Dict[str, Tuple[str str]]]]
    for chap_name in repeated_chapters:  # {'repeated_chapter': ('s_ts', 'e_ts')}
        begin, end = _compress(clip_list[chap_name][0], clip_list[chap_name][1])
        timestamps[chap_name] = (_f2ts(begin[0], clip=bdmv_clip), _f2ts(end[0] + 1, clip=bdmv_clip))
    for ep_num in tree:
        timestamps[ep_num] = {}  # {'episode': {'chapter': ('s_ts', 'e_ts')}}
        compressed = _compress(begins[ep_num], ends[ep_num])
        index = 0
        for chap_name in tree[ep_num]:
            if chap_name not in repeated_chapters:
                timestamps[ep_num][chap_name] = (_f2ts(compressed[0][index], clip=bdmv_clip), _f2ts(compressed[1][index] + 1, clip=bdmv_clip))
                index += 1
            else:
                timestamps[ep_num][chap_name] = timestamps[chap_name]

    # XML creation
    roots = {}
    for ep_num in tree:
        roots[ep_num] = ET.Element('Chapters')
        edition_entry = ET.SubElement(roots[ep_num], 'EditionEntry')
        ET.SubElement(edition_entry, 'EditionUID').text = str(randint(1, int(1E6)))
        ET.SubElement(edition_entry, 'EditionFlagDefault').text = '1'
        ET.SubElement(edition_entry, 'EditionFlagOrdered').text = '1'
        chapter_atoms = {}
        for chap_name in timestamps[ep_num]:
            chapter_atoms[chap_name] = ET.SubElement(edition_entry, 'ChapterAtom')
            ET.SubElement(chapter_atoms[chap_name], 'ChapterTimeStart').text = timestamps[ep_num][chap_name][0]
            ET.SubElement(chapter_atoms[chap_name], 'ChapterTimeEnd').text = timestamps[ep_num][chap_name][1]
            ET.SubElement(chapter_atoms[chap_name], 'ChapterUID').text = str(_chapter_uid_generator())

            if chap_name in repeated_chapters:
                ET.SubElement(chapter_atoms[chap_name], 'ChapterSegmentUID', format="hex").text = suids[chap_name]

            display = ET.SubElement(chapter_atoms[chap_name], 'ChapterDisplay')
            ET.SubElement(display, 'ChapterString').text = chap_name
            ET.SubElement(display, 'ChapterLanguage').text = 'eng'

    for root in roots:
        file = open(f'{root}_chapters.xml', 'xt')
        file.write('<?xml version="1.0"?>\n<!-- <!DOCTYPE Chapters SYSTEM "matroskachapters.dtd"> -->\n')
        file.write(ET.tostring(roots[root], encoding='unicode'))  # probably should have been achieved using ET.ElementTree.write() but this works too
        file.close()


def _segment_uid_generator() -> str:
    """Generates a 32 int long string for Mastroka SUIDs."""
    return str(int.from_bytes(urandom(16), byteorder))[:32]


def _chapter_uid_generator(k: int = 1) -> Union[int, List[int]]:
    """Random number generator for Mastroka chapters UIDs."""
    if k == 1:
        return choice(range(int(1E18), int(1E19)))
    return sample(range(int(1E18), int(1E19)), k)


def _f2ts(f: int, clip: vs.VideoNode) -> str:
    """Converts frame number to HH:mm:ss.nnnnnnnnn timestamp based on clip's framerate."""
    t = round(10 ** 9 * f * clip.fps ** -1)

    s = t / 10 ** 9
    m = s // 60
    s %= 60
    h = m // 60
    m %= 60

    return f'{h:02.0f}:{m:02.0f}:{s:012.9f}'


def _combine(a: List[int], b: List[int]) -> Tuple[List[int], List[int]]:
    """Eliminates continuous pairs: (a1,b1)(a2,b2) -> (a1,b2) if b1 == a2"""
    if len(a) != len(b):
        raise ValueError(f'{g(n())}: lists must be same length')
    if len(a) == 1 and len(b) == 1:
        return a, b

    ca, cb = [], []
    for i in range(len(a)):
        if i == 0:
            ca.append(a[i])
            if b[i] + 1 != a[i + 1]:
                cb.append(b[i])
            continue
        elif i < len(a) - 1:
            if a[i] - 1 != b[i - 1]:  # should we skip the start?
                ca.append(a[i])
            if b[i] + 1 != a[i + 1]:  # should we skip the end?
                cb.append(b[i])
            continue
        elif i == len(a) - 1:
            if a[i] - 1 != b[i - 1]:
                ca.append(a[i])
            cb.append(b[i])

    return ca, cb


def _compress(a: List[int], b: List[int]) -> Tuple[List[int], List[int]]:
    """Compresses lists to become continuous. (5,9)(12,14) -> (0,4)(7,9) -> (0,4)(5,7)"""
    if len(a) != len(b):
        raise ValueError(f'{g(n())}: lists must be same length')

    if a[0] > 0:  # shift all values so that 'a' starts at 0
        init = a[0]
        a = [i - init for i in a]
        b = [i - init for i in b]

    if len(a) == 1 and len(b) == 1:  # (5,9) -> (0,4)
        return a, b

    index, diff = 1, 0  # initialize this loop

    while index < len(a):
        for i in range(index, len(a)):
            if a[i] != b[i - 1] + 1:
                diff = a[i] - b[i - 1] - 1
                # we want to shift by one less than the difference so
                # the pairs become continuous

                index = i
                break

            diff = 0
            index += 1

        for i in range(index, len(a)):
            a[i] -= diff
            b[i] -= diff

    return a, b


# Decorator functions
g = lambda x: x[0][3]  # g(inspect.stack()) inside a function will print its name
