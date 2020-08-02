# ocsuite

Simple script designed to automate most of the Mastroka ordered chapters creation process.

TODO!

[acsuite.py]: https://github.com/OrangeChannel/acsuite


```py
from ocsuite import OC

import vapoursynth as vs
core = vs.core

src_clip = core.lsmas.LWLibavSource(r'/path/to/remuxed_BDMV.mkv')
src_audio = r'/path/to/remuxed_BDMV_audio.wav'

chapters = {  # see tests.py for more examples
    '01': {
        'Part A': 0,
        'Part B': 3861,
        'Middle Card': 20884,
        'Part C': (21004, 29696),
        'OP': 30042,
        'Part D': 32201,
        'Preview': (33686, 34045)
    },
    '02': {
        'Part A': 34070,
        'OP': 35748,
        'Part B': 37907,
        'Part C': 51429,
        'ED': 65048,
        'Part D': 67181,
        'Preview': (67733, 68092)
    },
    '03': {
        'Part A': 71578,
        'Part B': 84686,
        'Part C': (90000, 94982)
    }
}

oc = OC(chapters, ['OP', 'ED'])
clips = oc.clips(src_clip)

oc.cut_audio(src_clip, src_audio, r'/path/to/audio_dir/')
oc.write_to_xml(src_clip, r'/path/to/chapter_dir/')
print(oc.suids)
```

Outputs:

TODO!

---

## Getting Started

### Dependencies
- [acsuite.py] for cutting audio.
  - [FFmpeg](https://ffmpeg.org/)
  - [VapourSynth R49+](https://github.com/vapoursynth/vapoursynth/releases)
- [MKVToolNix](https://mkvtoolnix.download/downloads.html) for muxing chapters.

### Installing

#### Windows

1. Navigate to your Python installation folder (i.e. `C:\Python\`).
1. Download the `ocsuite.py` file to the site-packages folder (`C:\Python\Lib\site-packages\`).

#### Arch Linux

Install the [AUR package](https://aur.archlinux.org/packages/vapoursynth-tools-ocsuite-git/) `vapoursynth-tools-ocsuite-git` with your favorite AUR helper:

```sh
yay -S vapoursynth-tools-ocsuite-git
```

#### Gentoo Linux

Install via the [VapourSynth portage tree](https://github.com/4re/vapoursynth-portage).

---

## Working with Ordered Chapters

### Remuxing the BDMV

```sh
ffmpeg -i bluray:BDMV/../ -map 0 -c copy -c:a pcm_s16le volume01.mkv
ffmpeg -i bluray:BDMV/../ -map 0 -c copy -c:a pcm_s16le volume02.mkv
ffmpeg -i bluray:BDMV/../ -map 0 -c copy -c:a pcm_s16le volume03.mkv
ffmpeg -i 00007.m2ts -map 0 -c copy -c:a pcm_s16le OVA.mkv

mkvmerge -o full_remux.mkv volume01.mkv + volume02.mkv + volume03.mkv + OVA.mkv
```

TODO

## Help!

Read the docstrings included in `ocsuite.py` or
use Python's builtin `help`:

```py
help('ocsuite')
```

