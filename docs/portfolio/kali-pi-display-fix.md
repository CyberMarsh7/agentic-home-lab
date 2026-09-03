# Project: Raspberry Pi 3B + 3.5" SPI Touchscreen (Kali Linux)

**Stack:** Linux boot config (`config.txt`, device tree overlays), SPI/DRM
display drivers, systemd, network diagnostics

## The problem

A 3.5" ILI9486 + XPT2046 SPI touchscreen connected via GPIO showed nothing —
first a blank screen, then (after a partial fix) the Pi hanging at boot
entirely, then later a boot-loop. Multiple failure modes stacked on top of
each other across sessions, on hardware (Pi 3B + generic SPI screen) with no
single authoritative guide covering the exact combination.

## Root-cause path

1. First driver guess (`pitft35-resistive`) was wrong for this exact display
   chip — produced nothing.
2. Cross-referenced the actual hardware (XPT2046 touch controller + 480x320)
   against community reports to identify the real display chip as an
   ILI9486, then found a Raspberry Pi forum thread solving this precise
   combination with Bookworm-based OSes: the `piscreen,drm` overlay.
3. That produced a picture — upside down. Fixed via `rotate=180`.
4. The rotation fix then caused the Pi to hang at boot entirely. Diagnosed
   as a conflict between the SPI display driver and the default HDMI driver
   (`vc4-kms-v3d`) both trying to claim the primary display — disabling the
   HDMI driver (irrelevant anyway, since there's no HDMI monitor attached)
   resolved it.
5. Verified the fix was actually live on the physical SD card (not just
   written to a reference copy) by directly inspecting the mounted boot
   partition — caught and corrected a case where troubleshooting had drifted
   to the wrong physical drive letter after a second card was connected.
6. Diagnosed a Pi that appeared completely unresponsive (identical to having
   no SD card at all) by using ARP/subnet sweeps and MAC vendor-ID matching
   to determine whether the board was failing before Linux even started, or
   booting fine and only the display driver was silent — a meaningfully
   different problem requiring a different fix, resolved by process of
   elimination without needing a monitor or serial console.

## Result

Confirmed working: SPI/GPIO display active, correct orientation, HDMI driver
cleanly disabled, no boot hang, WiFi reconnecting automatically post-setup.
Documented as a reusable `config.txt` for future SD cards, with the full
decision trail recorded so the same dead ends aren't re-walked next time.
