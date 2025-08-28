# i3 Revamp Migration Checklist

- [ ] Switched chezmoi to branch `i3-revamp`
- [ ] Verified backup exists under `~/.config/i3/.bak_YYYYMMDD_HHMM`
- [ ] Enabled picom systemd user unit (optional):
      `systemctl --user enable --now picom.service`
- [ ] Reloaded i3 (Super+Shift+c)
- [ ] Verified audio keys (wpctl + i3blocks refresh)
- [ ] Verified screenshots (active monitor full, window, selection)
- [ ] Verified monitors (setup-monitors.sh) and removed static workspace mapping
- [ ] Verified printer status in bar (robust script)
- [ ] Verified printer manager works without hard-coded printer
- [ ] Verified Pi-hole block status (and click-to-toggle if token configured)
- [ ] Verified file manager autostart (Thunar) on workspace 4
- [ ] Verified Warp launcher and removed `warp-terminal-preview`
- [ ] Verified no duplicate/invalid i3 directives
- [ ] Reviewed README and switch-to-i3.sh updates
- [ ] Installed missing packages:
      `sudo pacman -S --needed - < ~/.config/i3/manjaro_packages_i3_revamp.txt`
- [ ] Happy with changes? Merge branch:
      `git -C ~/.local/share/chezmoi checkout main && git -C ~/.local/share/chezmoi merge i3-revamp`
- [ ] Unhappy? Run rollback:
      `~/bin/rollback_i3_changes.sh`

