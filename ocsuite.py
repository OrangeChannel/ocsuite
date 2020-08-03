"""Fully automated ordered chapters creation from a remuxed BDMV."""
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '3 August 2020'

import copy
import functools
import os
import pathlib
import random
import sys
import xml.etree.ElementTree as ET
from typing import Dict, Generator, List, Tuple, Union

import acsuite
import vapoursynth as vs

core = vs.core

_Slice = Tuple[int, int]
_Episode = Dict[str, Union[int, _Slice]]
_Path = Union[bytes, os.PathLike, pathlib.Path, str]


class Chapter:
    """
    A dataclass representing a chapter, to be put into a dictionary mapping names to Chapter instances.

    Guaranteed attributes when OC class is initiated are:
        'name' - string of the chapter's name (matches the dictionary mapping)
        'start_frame' - starting frame (inclusive)
        'end_frame' - ending frame (inclusive)

    When OC.write_to_xml is called, two more attributes are added:
        'start_ts' - string of the chapter's start frame converted to a timestamp in HH.mm.ss.nnnnnnnnn form
        'end_ts' - string of the chapter's (end frame + 1) converted to a timestamp in HH.mm.ss.nnnnnnnnn form
    """
    def __init__(self, name: str, start_frame: int):
        self.name = name
        self.start_frame = start_frame


class OC:
    """
    Base class for other related ordered chapters functions.

    `OC(...).main_tree` is a dictionary contained episodes and their chapter dictionaries of Chapter objects.
    `OC(...).suids` is a dictionary mapping repeated chapter names to their Mastroka segment UIDs (SUIDs),
    these are required to be muxed as the SUID for each of the repeated chapter MKVs
    in order for the chapter files to work properly.

    :param chap_dict:          dictionary of episode names (strings) to a dictionary of chapter names (strings) to ints or tuples of 2 ints
                                {'Episode 01': {'Part A': 10,   # starts on frame 10, ends on frame 19
                                                'Part B': 20,   # starts on frame 20, ends on frame 29
                                                'ED': (30, 39)  # starts on frame 30, ends on frame 39
                                                },
                                 'Episode 02': {'OP': 66,            # starts on frame 66, ends on frame 69
                                                'Part A': (70, 82),  # starts on frame 70, ends on frame 82
                                                'Part B': (90, 99)   # starts on frame 90, ends on frame 99
                                                }
                                 }
        See README.md for more examples.

        All chapters MUST have a start frame, but only the last chapter of each episode must have an ending frame.
        Frames are INCLUSIVE, so a Python slice of part_a=src[10:20] would start on frame 10, and end on frame 19.
        If there is no space between neighboring chapters,
        you DO NOT need to include the end frame for the first chapter,
        it will be assumed to be continuous with the next chapter (see example above).

        If only giving the start frame, ONLY provide a sole int.
        Last chapters of each episode MUST be given a tuple of (start frame, end frame) where the frame range is INCLUSIVE.

    :param repeated_chapters:  list of strings of names of chapters that are to be cut out of each episode that
                               contains them and then added back with an external segment reference
                               (i.e. `['OP', 'ED']` or `['OP']`)
    """
    def __init__(self, chap_dict: Dict[str, _Episode], repeated_chapters: List[str]):
        self.original_dict = chap_dict
        self.repeated_chapters = repeated_chapters

        main_tree: Dict[str, Dict[str, Chapter]] = {}

        for episode in chap_dict.keys():
            main_tree[episode] = {}
            chapter_frames = []
            for chap_name, chap_tuple in chap_dict[episode].items():
                if isinstance(chap_tuple, int):
                    chapter_frames.append([chap_tuple])
                elif isinstance(chap_tuple, tuple):
                    chapter_frames.append(list(chap_tuple))
            for index, name in enumerate(chap_dict[episode].keys()):
                main_tree[episode][name] = Chapter(name, chapter_frames[index][0])
                if len(chapter_frames[index]) == 2:
                    setattr(main_tree[episode][name], 'end_frame', chapter_frames[index][1])
                else:
                    try:
                        setattr(main_tree[episode][name], 'end_frame', chapter_frames[index+1][0] - 1)
                    except IndexError:
                        raise ValueError("last chapter of each episode must have an end frame") from None

        main_tree['_repeated_chapters'] = {}

        for ep_dict in main_tree.values():
            for name, chapter in ep_dict.items():
                if name in repeated_chapters:
                    main_tree['_repeated_chapters'][name] = copy.copy(chapter)

        self.main_tree = main_tree

        self.suids = {rchap_name: segment_uid_generator() for rchap_name in main_tree['_repeated_chapters']}

    def clips(self, src_clip: vs.VideoNode) -> Dict[str, vs.VideoNode]:
        """
        Returns dictionary of trimmed clips from a source clip.
        Repeated chapter keys will have a '_' (underscore) prepended to their names to avoid collisions with main episode names.

        :param src_clip:  VideoNode from a remuxed BDMV or something similar including all the frames the the chap_dict
                          provided to the class constructor.
        :return:          Dictionary of episode names (or repeated chapters names) to a trimmed clip (VideoNode)
                          not including the repeated chapters if found.
        """
        clip_dict = {}
        for ep_name, chap_dict in self.main_tree.items():
            if ep_name == '_repeated_chapters':
                for repeated_chap_name, rchap in chap_dict.items():
                    clip_dict['_' + repeated_chap_name] = src_clip[get_slice(rchap)]
            else:
                slices = []
                for chapter in chap_dict.values():
                    if chapter.name not in self.repeated_chapters:
                        slices.append(get_slice(chapter))
                segments = [src_clip[s] for s in slices]
                clip_dict[ep_name] = core.std.Splice(segments, mismatch=True)

        return clip_dict

    def cut_audio(self, src_clip: vs.VideoNode, audio_file: _Path, base_dir: _Path, *, ffmpeg_path: _Path = None, timecodes_file: _Path = None) -> None:
        """
        Cuts audio using acsuite.eztrim() via FFmpeg and a source audio file.

        Outputs audio files in the given directory with `base_dir`.

        Audio files will have the same extension
        (or be converted to WAV if extension not recognized by FFmpeg) as the input audio file.

        Audio files will be in the form of 'base_dir/{episode name}_cut.ext' where the episode name will be taken from the OC
        instance's clip dictionary, with repeated chapters being given their own cut audio file in the form of
        'base_dir/{repeated chap name}_cut.ext'.

        :param src_clip:     Source clip needed to determine frame rate to convert frame numbers into timestamps.
        :param audio_file:   Base audio file to trim/splice from. Extension and codec will be copied if possible,
                             otherwise re-encoded to WAV via FFmpeg.
        :param base_dir:     Base directory (ideally empty) to save cut audio files into. Must be an existing directory.
        :param ffmpeg_path:  Optional param to specify FFmpeg executable path is `ffmpeg` is not discoverable in your PATH for acsuite.eztrim().
        :param timecodes_file: Optional timecodes v2 file for acsuite.eztrim() to use to speed up VFR clips. Not needed as eztrim will fallback to a slower frames() method instead.
        """
        if not os.path.isdir(base_dir):
            raise NotADirectoryError(f"{base_dir} is not a valid existing directory")
        cwd = os.getcwd()
        os.chdir(base_dir)

        for ep_name, ep_dict in self.main_tree.items():
            if ep_name == '_repeated_chapters':
                for rchap in ep_dict.values():
                    s = get_slice(rchap)
                    acsuite.eztrim(src_clip, (s.start, s.stop), audio_file, rchap.name + '_cut', ffmpeg_path=ffmpeg_path, quiet=True, timecodes_file=timecodes_file)
            else:
                ep_frames = []
                for chapter in ep_dict.values():
                    if chapter.name not in self.repeated_chapters:
                        s = get_slice(chapter)
                        ep_frames.append([s.start, s.stop])
                acsuite.eztrim(src_clip, list(compress(ep_frames)), audio_file, ep_name + '_cut', ffmpeg_path=ffmpeg_path, quiet=True, timecodes_file=timecodes_file)

        os.chdir(cwd)

    def write_to_xml(self, src_clip: vs.VideoNode, base_dir: _Path, *, language: str = 'eng'):
        """
        Writes chapter files to XML files recognizable by the Mastroka container.

        The repeated chapters will be inserted into the virtual timeline via external segment references
        using SUIDs that you will need to mux the repeated chapter files with (can be obtained via OC.suids).

        Chapter files will be saved in the form of 'base_dir/{episode name}_chapters.xml'.

        :param src_clip:  Source clip to determine frame rate to convert frame numbers into timestamps.
        :param base_dir:  Base directory (ideally empty) to save chapter files into. Must be an existing directory.
        :param language:  Mastroka language identifier for chapter names.
            Must be from the 3 letters bibliographic ISO-639-2 list at <https://www.loc.gov/standards/iso639-2/php/English_list.php>.
            Might support BCP 47 in the future but this should suffice for now. Defaults to 'eng' or English.
        """
        if not os.path.isdir(base_dir):
            raise NotADirectoryError(f"{base_dir} is not a valid existing directory")
        cwd = os.getcwd()
        os.chdir(base_dir)

        clips = self.clips(src_clip)

        for repeated_chapter in self.main_tree['_repeated_chapters'].values():
            slice_ = get_slice(repeated_chapter)
            corrected_frames = next(squeeze([[slice_.start, slice_.stop]]))
            clip = clips['_' + repeated_chapter.name]
            ts = functools.partial(acsuite.f2ts, precision=9, src_clip=clip)
            setattr(repeated_chapter, 'start_ts', ts(corrected_frames[0]))
            setattr(repeated_chapter, 'end_ts', ts(corrected_frames[1]))

        for ep_name, chap_dict in self.main_tree.items():
            clip = clips[ep_name]
            ts = functools.partial(acsuite.f2ts, precision=9, src_clip=clip)
            frames = []
            for chapter in chap_dict.values():
                if chapter.name not in self.repeated_chapters:
                    slice_ = get_slice(chapter)
                    frames.append([slice_.start, slice_.stop])
            corrected_frames = squeeze(frames)
            for chapter in chap_dict.values():
                if chapter.name not in self.repeated_chapters:
                    frames = next(corrected_frames)
                    setattr(chapter, 'start_ts', ts(frames[0]))
                    setattr(chapter, 'end_ts', ts(frames[1]))
                else:
                    setattr(chapter, 'start_ts', self.main_tree['_repeated_chapters'][chapter.name].start_ts)
                    setattr(chapter, 'end_ts', self.main_tree['_repeated_chapters'][chapter.name].end_ts)

        roots = {}
        for ep_name, chap_dict in self.main_tree.items():
            if not ep_name.startswith('_'):
                roots[ep_name] = ET.Element('Chapters')

                edition_entry = ET.SubElement(roots[ep_name], 'EditionEntry')
                ET.SubElement(edition_entry, 'EditionUID').text = str(random.randint(1, int(1E6)))
                ET.SubElement(edition_entry, 'EditionFlagDefault').text = '1'
                ET.SubElement(edition_entry, 'EditionFlagOrdered').text = '1'

                for chapter in chap_dict.values():
                    chap_atom = ET.SubElement(edition_entry, 'ChapterAtom')
                    ET.SubElement(chap_atom, 'ChapterTimeStart').text = chapter.start_ts
                    ET.SubElement(chap_atom, 'ChapterTimeEnd').text = chapter.end_ts
                    ET.SubElement(chap_atom, 'ChapterUID').text = chapter_uid_generator()

                    if chapter.name in self.repeated_chapters:
                        ET.SubElement(chap_atom, 'ChapterSegmentUID', format="hex").text = self.suids[chapter.name]

                    display = ET.SubElement(chap_atom, 'ChapterDisplay')
                    ET.SubElement(display, 'ChapterString').text = chapter.name
                    ET.SubElement(display, 'ChapterLanguage').text = language

        for root_name, root in roots.items():
            file = open(f'{root_name}_chapters.xml', 'xt')
            file.write('<?xml version="1.0"?>\n<!-- <!DOCTYPE Chapters SYSTEM "matroskachapters.dtd"> -->\n')
            file.write(ET.tostring(root, encoding='unicode'))
            file.close()

        os.chdir(cwd)


def get_slice(chapter_: Chapter) -> slice:
    """Change chapter start and end frame into a slice."""
    return slice(getattr(chapter_, 'start_frame'), getattr(chapter_, 'end_frame') + 1)


def compress(pairs: List[List[int]]) -> Generator[Tuple[int, int], None, None]:
    """[[1, 2], [3, 4], [4, 5]] -> [(1, 2), (3, 5)]"""
    it = iter(pairs)
    q = tuple(next(it))
    for p in map(tuple, it):
        if q[1] == p[0]:
            q = q[0], p[1]
        else:
            yield q
            q = p
    yield q


def squeeze(pairs: List[List[int]], /, _start: int = 0) -> Generator[List[int], None, None]:
    """[[10, 20], [25, 35], [35, 45], [50, 60]] -> [[0, 10], [10, 20], [20, 30], [30, 40]]"""
    for a, b in pairs:
        yield [_start, (_start := _start + b - a)]


def segment_uid_generator() -> str:
    """Generates a 32 int long string for Mastroka SUIDs."""
    return str(int.from_bytes(os.urandom(16), sys.byteorder))[:32]


def chapter_uid_generator() -> str:
    """Random number generator for Mastroka chapter UIDs."""
    return str(random.choice(range(int(1E18), int(1E19))))

