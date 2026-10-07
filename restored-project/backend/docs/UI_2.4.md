# ALI AI 2.4 — Professional Assistant UI Contract

## Visual target

The desktop shell follows the supplied `ali_agent_ui.py` reference rather than reproducing its placeholder-only behavior. The target is a clean Windows workstation layout with:

- white main surface;
- light-gray navigation rail;
- thin dividers;
- restrained blue action/status accent;
- green/red/amber semantic status colors;
- Segoe UI;
- flat controls and subtle hover feedback;
- clear three-zone hierarchy;
- compact status bar.

## Direction contract

Arabic (`ar`, `ar-SA`, `ar-YE`, etc.):

`navigation RIGHT → center → inspector LEFT`

English (`en`, `en-US`, etc.):

`navigation LEFT → center → inspector RIGHT`

Text justification, composer alignment, list alignment, editor gutter/scrollbar position and action-button ordering mirror the same direction.

## No mixed-direction regressions

Paths, code, URLs, hashes and identifiers remain LTR islands inside both languages. Natural-language containers use the active direction. The application must never reverse a file path, hash, command, or source URL merely because the surrounding UI is Arabic.

## Responsive behavior

At 1480×920 and above, the full three-pane workspace is visible. Between 1120×720 and 1479×919, pane widths become adaptive. Below the minimum window size, the application keeps a usable center chat area and exposes the right/left inspector through a collapsible notebook rather than allowing important controls to disappear.

## Startup behavior

The desktop shell starts without loading heavyweight model/training services. Hardware probing is cached/lazy. The shell is usable before a model is installed and reports the missing capability honestly.

## Acceptance

A UI build is accepted only when:

1. Arabic starts mirrored.
2. English starts unmirrored.
3. Switching language rebuilds without losing the current conversation ID.
4. Arabic prose is right-justified while code/path islands remain readable LTR.
5. User messages remain visually right-aligned and assistant messages left-aligned in both languages.
6. Editor line numbers and scrollbars mirror with the language.
7. No callback references destroyed widgets after language switching.
8. Main UI can start with no model present.
## Native Windows bidi test

Before marking a Windows release verified, the installer must run the app natively and exercise Arabic typing, Arabic response rendering, English typing, English response rendering, language switching, file paths, PowerShell commands and mixed Arabic/code content. A Linux/X11 screenshot is not considered evidence for native Windows complex-script rendering.
