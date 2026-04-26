"""Theme CSS generation and iOS-style toggle widget."""

from __future__ import annotations

import ipywidgets as widgets


def _theme_css(pid: str, dark: bool) -> str:
    if dark:
        bg      = "#1e1e2e"; card    = "#181825"; border  = "#313244"
        text    = "#cdd6f4"; muted   = "#a6adc8"; accent  = "#89b4fa"
        tog_off = "#45475a"; hr_col  = "#313244"
        warn_bg = "#2a2030"; warn_bdr = "#f38ba8"; warn_txt = "#f38ba8"
        inp_bg  = "#232334"
    else:
        bg      = "#f4f4f9"; card    = "#ffffff"; border  = "#e4e4eb"
        text    = "#1e1e2e"; muted   = "#6b7280"; accent  = "#6366f1"
        tog_off = "#d1d5db"; hr_col  = "#e4e4eb"
        warn_bg = "#fffbf0"; warn_bdr = "#f5a623"; warn_txt = "#7a5300"
        inp_bg  = "#ffffff"

    accent_glow = accent + "33"  # 20 % opacity for focus ring

    return f"""<style>
/* ── mplstudio {pid} ── */
.mpl-s-{pid} {{
  --mpl-accent:{accent};
  background:{bg};border-radius:16px;box-sizing:border-box;overflow:hidden;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  color:{text};
}}
.mpl-c-{pid} {{
  background:{card};border:1px solid {border};border-radius:12px;
  box-sizing:border-box;overflow:hidden;
}}
.mpl-t-{pid} {{
  display:block;margin-bottom:6px;font-size:0.75em;font-weight:700;
  letter-spacing:0.07em;text-transform:uppercase;color:{muted};
}}
/* sliders */
.mpl-s-{pid} .widget-slider .ui-slider {{
  background:{border};border:none;border-radius:4px;
}}
.mpl-s-{pid} .widget-slider .ui-slider .ui-slider-handle {{
  background:{accent};border:none;border-radius:50%;
  width:14px;height:14px;top:-4px;cursor:pointer;
  box-shadow:0 1px 4px rgba(0,0,0,.25);
}}
/* slider readout — compact editable input */
.mpl-s-{pid} .widget-readout {{
  background:{inp_bg} !important;
  border:1.5px solid {border} !important;
  border-radius:6px !important;
  color:{text} !important;
  padding:1px 5px !important;
  min-width:44px !important;
  max-width:52px !important;
  width:52px !important;
  height:22px !important;
  line-height:20px !important;
  box-sizing:border-box !important;
  box-shadow:inset 0 1px 2px rgba(0,0,0,.07) !important;
  font-size:0.82em !important;
}}
/* text / number inputs */
.mpl-s-{pid} input[type=text],
.mpl-s-{pid} input[type=number] {{
  background:{inp_bg} !important;
  color:{text} !important;
  border:1.5px solid {border} !important;
  border-radius:6px !important;
  box-shadow:inset 0 1px 2px rgba(0,0,0,.07) !important;
}}
.mpl-s-{pid} input[type=text]:focus,
.mpl-s-{pid} input[type=number]:focus,
.mpl-s-{pid} .widget-readout:focus {{
  border-color:{accent} !important;
  box-shadow:0 0 0 3px {accent_glow},inset 0 1px 2px rgba(0,0,0,.07) !important;
  outline:none !important;
}}
/* dropdowns — appearance:none + ::after chevron */
.mpl-s-{pid} .widget-dropdown {{
  position:relative;
}}
.mpl-s-{pid} .widget-dropdown select {{
  -webkit-appearance:none;-moz-appearance:none;appearance:none;
  background:{card} !important;
  color:{text} !important;
  border:1.5px solid {border} !important;
  border-radius:8px !important;
  padding:3px 28px 3px 10px !important;
  cursor:pointer;
  font-size:0.88em;
  transition:border-color 0.15s;
}}
.mpl-s-{pid} .widget-dropdown select:focus {{
  border-color:{accent} !important;
  box-shadow:0 0 0 3px {accent_glow} !important;
  outline:none !important;
}}
.mpl-s-{pid} .widget-dropdown::after {{
  content:'▾';
  position:absolute;right:8px;top:50%;
  transform:translateY(-50%);
  color:{muted};pointer-events:none;
  font-size:16px;line-height:1;
}}
/* toggle buttons group */
.mpl-s-{pid} .widget-toggle-buttons .widget-toggle-button {{
  background:{card} !important;border-color:{border} !important;
  color:{text} !important;border-radius:8px !important;
  font-size:0.85em;transition:background 0.15s,color 0.15s;
}}
.mpl-s-{pid} .widget-toggle-buttons .widget-toggle-button.mod-active {{
  background:{accent} !important;border-color:{accent} !important;
  color:#fff !important;box-shadow:none;
}}
/* info/action button */
.mpl-s-{pid} .widget-button.mod-info {{
  background:{accent} !important;border-color:{accent} !important;
  color:#fff !important;border-radius:8px !important;box-shadow:none;
}}
/* collapsible per-* button — light accent tint background */
.mpl-per-{pid} button {{
  background:{accent}22 !important;
  border:1.5px solid {accent}66 !important;
  border-radius:8px !important;
  color:{text} !important;
  font-size:0.82em !important;
  padding:4px 10px !important;
  width:100% !important;
  text-align:left !important;
  box-shadow:none !important;
  cursor:pointer !important;
}}
.mpl-per-{pid} button:hover {{
  background:{accent}33 !important;
  border-color:{accent} !important;
}}
/* checkbox accent */
.mpl-s-{pid} .widget-checkbox input {{ accent-color:{accent}; }}
/* hr */
.mpl-s-{pid} hr {{ border-color:{hr_col}; }}
/* warning block */
.mpl-w-{pid} {{
  background:{warn_bg};border:1px solid {warn_bdr};color:{warn_txt};
  border-radius:12px;padding:8px 12px;font-size:0.9em;line-height:1.7;
}}
.mpl-w-{pid} .avail code {{
  background:{border};color:{muted};
  padding:1px 4px;border-radius:3px;font-size:0.88em;
}}
/* iOS-style actual-size toggle */
.mpl-ios-{pid} {{
  display:inline-flex;align-items:center;gap:7px;
  cursor:pointer;vertical-align:middle;user-select:none;
}}
.mpl-ios-{pid} .trk {{
  position:relative;width:40px;height:22px;
  background:{tog_off};border-radius:11px;
  transition:background 0.25s;flex-shrink:0;
}}
.mpl-ios-{pid} .thm {{
  position:absolute;width:18px;height:18px;
  background:#fff;border-radius:50%;top:2px;left:2px;
  transition:left 0.25s;box-shadow:0 1px 3px rgba(0,0,0,.3);
}}
.mpl-ios-{pid}.on .trk {{ background:{accent}; }}
.mpl-ios-{pid}.on .thm {{ left:20px; }}
.mpl-ios-{pid} .lbl {{ font-size:13px;color:{muted}; }}
</style>"""


def _ios_toggle(cb_model_id: str, label: str, pid: str, sfx: str) -> widgets.HTML:
    """iOS toggle wired to a hidden Checkbox. Uses single-quoted onclick to avoid attribute termination."""
    eid = f"mpl-ios-{pid}-{sfx}"
    # Single-quoted onclick so double-quotes work freely inside the JS.
    # \\\" in the f-string becomes \" in the HTML → escaped double-quote inside JS string.
    return widgets.HTML(
        f'<span id="{eid}" class="mpl-ios-{pid}" '
        f'onclick=\'var el=document.getElementById("{eid}");'
        f'el.classList.toggle("on");'
        f'var on=el.classList.contains("on");'
        f'var cb=document.querySelector("[data-model-id=\\"{cb_model_id}\\"] input[type=checkbox]");'
        f'if(cb){{cb.checked=on;cb.dispatchEvent(new Event("change",{{bubbles:true}}))}}'
        f'\'>'
        f'<span class="trk"><span class="thm"></span></span>'
        f'<span class="lbl">{label}</span></span>'
    )
