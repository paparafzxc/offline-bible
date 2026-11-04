# Filipino / Tagalog translation plan

Stillword v0.2 will support these two redistributable Tagalog editions first. Both are separate from the English WEB/ASV source pipeline.

## 1. Ang Dating Biblia (1905) — ADB1905

- Language: Tagalog (`tl`)
- Canon: 66-book Protestant canon
- Rights basis: listed as public domain by STEP Bible and by the public Bible-data source below.
- STEP Bible version/copyright information: https://www.stepbible.org/version.jsp?version=TagAngBiblia
- Dataset source listing: https://github.com/fangniude/bible-data/blob/translations/README.md
- Dataset archive: https://github.com/fangniude/bible-data/raw/refs/heads/master/bibledata-tl-adb1905.zip
- Import gate: inspect archive contents and exact source/version metadata; map verse IDs to Stillword OSIS identifiers; verify 66 books, chapter coverage, verse numbering, and sample references against an independent reader before marking complete.

## 2. Tagalog Unlocked Literal Bible (TGLULB, 2018)

- Language: Tagalog (`tl`)
- Publisher/community: Door43 World Missions Community
- Rights: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
- eBible edition details and download formats: https://ebible.org/find/details.php?id=tglulb
- eBible source archive: https://ebible.org/Scriptures/tglulb_usfm.zip
- STEP Bible copyright record: https://www.stepbible.org/version.jsp?version=TglULB
- Required attribution: Tagalog Unlocked Literal Bible © 2018 Door43 World Missions Community, licensed under CC BY-SA 4.0.
- ShareAlike: adaptations must be distributed under CC BY-SA 4.0. Keep text unaltered where possible; identify changes and do not imply Door43 endorses them.
- Import gate: parse official USFM archive, retain book/chapter/verse identifiers, validate canon coverage and verse numbering, and preserve attribution/license with the generated corpus.

## Not included without permission

The following are copyrighted Philippine Bible Society translations and must not be bundled in full until written permission is secured:

- Ang Biblia 2001 (ABTAG2001)
- Magandang Balita Biblia (MBBTAG / MBB05)
- Ang Salita ng Diyos (SND)

A quotation allowance (including the 500-verse threshold published for some PBS versions) is not a blanket license to distribute an entire Bible translation in an offline app. PBS lists translation/copyright permission as a request category: https://bible.org.ph/contact-us/

## Current implementation status

This file records candidates and import requirements. It does not claim the Tagalog text has already been imported. A translation is considered installed only after its actual text corpus is bundled and automated validation passes.
