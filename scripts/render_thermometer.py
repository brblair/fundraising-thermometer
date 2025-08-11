--- a/scripts/render_thermometer.py
+++ b/scripts/render_thermometer.py
@@
 DATA = pathlib.Path("data/funds.json")
 OUT  = pathlib.Path("thermometer.svg")
 COLS = 10
 SEG_GOAL = 1_000_000
 W, H = 1240, 420
+FILL_COLOR = "#e02020"  # bright red
@@
-    svg.append('<defs>')
-    svg.append('<style>.title{font:700 20px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#111}.label{font:600 13px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#222}.value{font:700 16px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#111}.tickMajor{stroke:#555}.tickMinor{stroke:#888}.tube{fill:none;stroke:#999;stroke-width:1.1}.segLbl{font:600 12px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#666}</style>')
-    # Per-column vertical gradients (red->green), revealed by level
-    for i in range(COLS):
-        svg.append(f'<linearGradient id="grad{i}" x1="0" y1="1" x2="0" y2="0"><stop offset="0%" stop-color="#d0021b"/><stop offset="100%" stop-color="#27ae60"/></linearGradient>')
-    # Tube FX: subtle inner shadow + outer glow
+    svg.append('<defs>')
+    svg.append('<style>.title{font:700 20px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#111}.label{font:600 13px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#222}.value{font:700 16px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#111}.tickMajor{stroke:#555}.tickMinor{stroke:#888}.tube{fill:none;stroke:#666;stroke-width:1.3}.segLbl{font:600 12px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#666}</style>')
+    # Tube FX: subtle inner shadow + outer glow (kept)
     svg.append('''<filter id="tubeFX" x="-25%" y="-25%" width="150%" height="150%" color-interpolation-filters="sRGB">
@@
     svg.append('</defs>')
@@
-        # Transparent tube and bulb (stroke only)
-        svg.append(f'<rect x="{rect_x}" y="{rect_y}" rx="12" ry="12" width="{rect_w}" height="{rect_h}" class="tube"/>' )
-        svg.append(f'<circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r}" class="tube"/>' )
-
-        # Define clip path for the thermometer shape (tube + bulb)
-        svg.append(f'<clipPath id="clipShape{i}">')
-        svg.append(f'  <rect x="{rect_x}" y="{rect_y}" rx="12" ry="12" width="{rect_w}" height="{rect_h}"/>\n  <circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r}"/>' )
-        svg.append(f'</clipPath>')
-
-        # Define clip path for the current level (from bottom up)
-        svg.append(f'<clipPath id="clipLevel{i}">')
-        svg.append(f'  <rect x="{bar_x-2}" y="{level_y}" width="{bar_w+4}" height="{level_h}"/>' )
-        svg.append(f'</clipPath>')
-
-        # Draw gradient fill for the full shape, then reveal only the funded height
-        # Nest the level clip inside the shape clip to get intersection
-        svg.append(f'<g clip-path="url(#clipShape{i})">')
-        svg.append(f'  <rect x="{rect_x}" y="{shape_top}" width="{rect_w}" height="{shape_h}" fill="url(#grad{i})" clip-path="url(#clipLevel{i})"/>' )
-        svg.append(f'</g>')
+        # Unified shape clip (tube + bulb)
+        svg.append(f'<clipPath id="clipShape{i}"><rect x="{rect_x}" y="{rect_y}" rx="12" ry="12" width="{rect_w}" height="{rect_h}"/><circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r}"/></clipPath>')
+        # 1) Base interior: white (unified look)
+        svg.append(f'<g clip-path="url(#clipShape{i})"><rect x="{rect_x}" y="{shape_top}" width="{rect_w}" height="{shape_h}" fill="#ffffff"/></g>')
+        # 2) Solid red fill revealed from bottom up (replaces white as it grows)
+        svg.append(f'<clipPath id="clipLevel{i}"><rect x="{bar_x-2}" y="{level_y}" width="{bar_w+4}" height="{level_h}"/></clipPath>')
+        svg.append(f'<g clip-path="url(#clipShape{i})"><rect x="{rect_x}" y="{shape_top}" width="{rect_w}" height="{shape_h}" fill="{FILL_COLOR}" clip-path="url(#clipLevel{i})"/></g>')
+        # 3) Outline on top with depth
+        svg.append(f'<g filter="url(#tubeFX)"><rect x="{rect_x}" y="{rect_y}" rx="12" ry="12" width="{rect_w}" height="{rect_h}" class="tube"/><circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r}" class="tube"/></g>')
