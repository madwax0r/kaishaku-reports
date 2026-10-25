# kaishaku-reports

Public test reports and scam tips for [kaishaku.ch](https://kaishaku.ch), an independent index of open-source PS4 and PS5 translation layers and a blacklist of fake "emulator" downloads.

Anyone can send a report here by pull request. Merged reports are imported into the site's compatibility matrix once a day.

## What belongs here

- **Compatibility reports.** One file per test of one title on one verified translation layer.
- **Scam tips.** Open an issue with the "Scam tip" form. A person reviews every tip before anything reaches the blacklist, because listing a site is a public accusation.

## What never belongs here

This repository opposes software piracy. A pull request or issue is closed without discussion if it contains, or links to:

- game files, disc images, `fPKG` packages, torrents, magnet links or file-sharing hosts;
- Sony firmware, system modules, BIOS files, encryption keys or exploit payloads, or instructions for extracting them;
- downloads of anything, including the translation layers themselves. Link to a layer's own GitHub repository instead.

Proof links may only point to **github.com** (an issue or pull request) or **youtube.com** (unedited test footage).

## Adding a compatibility report

1. Copy [`templates/report.md`](templates/report.md) to `reports/<layer>/<serial>-<os>-<yyyy-mm-dd>.md`, for example `reports/KytyPS5/PPSA01234-linux-2026-10-25.md`.
2. Fill in every field. Write `Not reported` for a detail you don't know. Never guess.
3. Open a pull request. An automatic check validates every report against these rules, then a maintainer reviews it. You can run the same check yourself first with `python3 scripts/validate.py`.

### Fields

| Field | Required | Notes |
|---|---|---|
| `title` | yes | Game title as published |
| `serial` | yes | `PPSA` or `CUSA` followed by five digits, e.g. `PPSA01234` |
| `layer` | yes | A layer on the site's verified list: `KytyPS5`, `SharpEmu`, `RPCSX` or `AnyPS5` |
| `status` | yes | One of the tiers below |
| `commit` | yes | Full or short commit SHA of the build you tested. If you only know a version number, put it in `version` and leave `commit` empty; the site then marks the row "commit not stated" |
| `version` | no | The build or version name, exactly as shown |
| `host_os` | yes | e.g. `Windows 11 24H2`, `Linux 6.11 (Fedora 41)`, `macOS 15.1` |
| `gpu` | yes | e.g. `AMD Radeon RX 7900 XT` |
| `driver` | yes | GPU or Vulkan driver version, e.g. `Mesa 24.2.4` |
| `tested_date` | yes | `YYYY-MM-DD` |
| `proof_url` | yes | A github.com issue or pull request, or an unedited youtube.com video, showing this test |

### Status tiers

| Status | Meaning |
|---|---|
| `Nothing` | Crashes on initialization |
| `Boots` | Initializes the executable and logs syscalls; no graphics |
| `Intro` | Renders splash screens, shaders or menus via Vulkan before hanging |
| `Ingame` | Reaches interactive rendering with graphical or audio defects |
| `Playable` | Completes start to finish without fatal crashes |

Pick the highest tier the proof actually shows. `Playable` needs evidence of a complete run.

## Held-back projects

Projects that need Sony firmware, system modules or keys to run (currently shadPS4 and Prosperity) are not on the verified list, so reports for them can't be accepted here. See the Registry section of the site for the reasons.

## License

GNU Affero General Public License v3.0. See [LICENSE](LICENSE). By opening a pull request you agree that your contribution is released under it.

PlayStation, PS4 and PS5 are trademarks of Sony Interactive Entertainment Inc., named here only to describe software compatibility. This project is not affiliated with or endorsed by Sony.
