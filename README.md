# ocsuite

Simple script designed to automate most of the Mastroka ordered chapters creation process.

- Uses [acsuite.py][] to cut the audio from a remuxed + combined BDMV.
- Generates a VapourSynth script for splitting the remux into clips.
- Generates chapter files (.xml) for each episode (automatically adds the repeated chapters as ordered chapter references with a generated SUID).

[acsuite.py]: https://github.com/OrangeChannel/acsuite


## Functions:

### ordered_chapters(chapters, repeated_chapters, remuxed_bdmv, save_vs_clips_to_file)

```py
from ocsuite import ordered_chapters

chapters = {  # inclusive
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
    '02|Preview':     (67733, 68092),

    '03|Part A':      (68117, 70058),
    '03|OP':          (70059, 72217),
    '03|Part B':      (72218, 81784),
    '03|Middle Card': (81785, 81904),
    '03|Part C':      (81905, 98590),
    '03|ED':          (98591, 100725),
    '03|Part D':      (100726, 101779),
    '03|Preview':     (101780, 102139),

    '04|Part A':      (102164, 104729),
    '04|OP':          (104730, 106886),
    '04|Part B':      (106887, 120887),
    '04|Middle Card': (120888, 121007),
    '04|Part C':      (121008, 133139),
    '04|ED':          (133140, 135272),
    '04|Part D':      (135273, 135824),
    '04|Preview':     (135825, 136184),

    '05|Part A':      (136209, 137048),
    '05|OP':          (137049, 139205),
    '05|Part B':      (139206, 151266),
    '05|Middle Card': (151267, 151386),
    '05|Part C':      (151387, 167474),
    '05|ED':          (167475, 169607),
    '05|Part D':      (169608, 169871),
    '05|Preview':     (169872, 170231),

    '06|Part A':      (170256, 171957),
    '06|OP':          (171958, 174116),
    '06|Part B':      (174117, 187231),
    '06|Middle Card': (187232, 187351),
    '06|Part C':      (187352, 200512),
    '06|ED':          (200513, 202647),
    '06|Part D':      (202648, 203917),
    '06|Preview':     (203918, 204277),

    '07|Part A':      (204302, 205405),
    '07|OP':          (205406, 207562),
    '07|Part B':      (207563, 225999),
    '07|Middle Card': (226000, 226119),
    '07|Part C':      (226120, 235519),
    '07|ED':          (235520, 237652),
    '07|Part D':      (237653, 237964),
    '07|Preview':     (237965, 238324),

    '08|Part A':      (238349, 242281),
    '08|OP':          (242282, 244438),
    '08|Part B':      (244439, 254892),
    '08|Middle Card': (254893, 255012),
    '08|Part C':      (255013, 268797),
    '08|ED':          (268798, 270932),
    '08|Part D':      (270933, 272010),
    '08|Preview':     (272011, 272370),

    '09|Part A':      (272395, 273114),
    '09|OP':          (273115, 275272),
    '09|Part B':      (275273, 283975),
    '09|Middle Card': (283976, 284095),
    '09|Part C':      (284096, 303395),
    '09|ED':          (303396, 305528),
    '09|Part D':      (305529, 306056),
    '09|Preview':     (306057, 306416),

    '10|Part A':      (306443, 307232),
    '10|OP':          (307233, 309389),
    '10|Part B':      (309390, 322888),
    '10|Middle Card': (322889, 323008),
    '10|Part C':      (323009, 336601),
    '10|ED':          (336602, 338736),
    '10|Part D':      (338737, 340102),
    '10|Preview':     (340103, 340462),

    '11|Part A':      (340487, 340774),
    '11|OP':          (340775, 342932),
    '11|Part B':      (342933, 359378),
    '11|Middle Card': (359379, 359498),
    '11|Part C':      (359499, 369568),
    '11|ED':          (369569, 371702),
    '11|Part D':      (371703, 374147),
    '11|Preview':     (374148, 374507),

    '12|Part A':      (374545, 408744),

    'OVA|OP':                                   (408769, 410926),
    'OVA|Part 1: You Never Let Us Down':        (410927, 425142),
    'OVA|Card 1':                               (425143, 425262),
    'OVA|Part 2: Always Growing Closer':        (425263, 426565),
    'OVA|Card 2':                               (426566, 426709),
    'OVA|Part 3: Let\'s Change You Into This!': (426710, 435939),
    'OVA|Card 3':                               (435940, 436059),
    'OVA|Part 4: I\'m Your Big Sister':         (436060, 439242),
    'OVA|ED':                                   (439243, 441376)
}

file = r'/path/to/remuxed_bdmv.mkv'

ordered_chapters(chapters, ['OP', 'ED'], file)
```

Outputs:
```py
import vapoursynth as vs
core = vs.core
bdmv = core.lsmas.LWLibavSource(r'/path/to/remuxed_bdmv.mkv')
ep01=bdmv[0:30042]+bdmv[32201:34046]
ep02=bdmv[34070:35748]+bdmv[37907:65048]+bdmv[67181:68093]
ep03=bdmv[68117:70059]+bdmv[72218:98591]+bdmv[100726:102140]
ep04=bdmv[102164:104730]+bdmv[106887:133140]+bdmv[135273:136185]
ep05=bdmv[136209:137049]+bdmv[139206:167475]+bdmv[169608:170232]
ep06=bdmv[170256:171958]+bdmv[174117:200513]+bdmv[202648:204278]
ep07=bdmv[204302:205406]+bdmv[207563:235520]+bdmv[237653:238325]
ep08=bdmv[238349:242282]+bdmv[244439:268798]+bdmv[270933:272371]
ep09=bdmv[272395:273115]+bdmv[275273:303396]+bdmv[305529:306417]
ep10=bdmv[306443:307233]+bdmv[309390:336602]+bdmv[338737:340463]
ep11=bdmv[340487:340775]+bdmv[342933:369569]+bdmv[371703:374508]
ep12=bdmv[374545:408745]
epOVA=bdmv[410927:439243]
OP=bdmv[30042:32201]  # SUID: 28958754654319819755798014595776
ED=bdmv[65048:67181]  # SUID: 11569449511598453506872648520663
```
---

## Getting Started

### Dependencies
- [Python 3.8+](https://www.python.org/downloads/)
- [acsuite.py]
  - [VapourSynth](https://github.com/vapoursynth/vapoursynth/releases)
  - [MKVToolNix](https://mkvtoolnix.download/downloads.html)

### Installing

#### Windows

1. Navigate to your Python installation folder (i.e. `C:\Python\`).
1. Download the `ocsuite.py` file to the site-packages folder (`C:\Python\Lib\site-packages\`).

#### Arch Linux

TODO
<!--
Install the [AUR package]() `vapoursynth-plugin-ocsuite-git` with your favorite AUR helper:

```sh
yay -S vapoursynth-plugin-ocsuite-git
```
-->

#### Gentoo Linux

TODO
<!--
Install via the [VapourSynth portage tree](https://github.com/4re/vapoursynth-portage).
-->
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

Use python's builtin `help`: 

```py
help('ocsuite')
```

