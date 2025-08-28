#!/usr/bin/env python3
"""
Generate a visual cheat sheet for i3 keybindings
Creates both terminal and graphical versions
"""

import json
from pathlib import Path
from typing import List, Dict

class CheatSheetGenerator:
    def __init__(self):
        self.essential_bindings = {
            '🚀 Launch': [
                ('$mod+Return', 'Terminal'),
                ('$mod+d', 'App Launcher'),
                ('$mod+Shift+b', 'Browser'),
            ],
            '🪟 Windows': [
                ('$mod+Shift+q', 'Kill Window'),
                ('$mod+h/j/k/l', 'Focus Direction'),
                ('$mod+Shift+h/j/k/l', 'Move Window'),
                ('$mod+f', 'Fullscreen'),
                ('$mod+Shift+Space', 'Toggle Float'),
            ],
            '🖥️ Workspaces': [
                ('$mod+1-0', 'Switch to WS'),
                ('$mod+Shift+1-0', 'Move to WS'),
                ('$mod+Tab', 'Next WS'),
                ('$mod+Shift+Tab', 'Prev WS'),
            ],
            '📐 Layout': [
                ('$mod+v', 'Split Vertical'),
                ('$mod+b', 'Split Horizontal'),
                ('$mod+s', 'Stacking'),
                ('$mod+w', 'Tabbed'),
                ('$mod+e', 'Toggle Split'),
            ],
            '⚙️ System': [
                ('$mod+Shift+c', 'Reload Config'),
                ('$mod+Shift+r', 'Restart i3'),
                ('$mod+Shift+e', 'Exit i3'),
                ('$mod+Shift+x', 'Lock Screen'),
            ],
            '📷 Media': [
                ('Print', 'Screenshot'),
                ('Shift+Print', 'Area Screenshot'),
                ('XF86AudioRaiseVolume', 'Volume Up'),
                ('XF86AudioLowerVolume', 'Volume Down'),
            ]
        }
    
    def generate_terminal_cheatsheet(self) -> str:
        """Generate a compact terminal cheat sheet"""
        output = []
        output.append("╔" + "═" * 58 + "╗")
        output.append("║" + " i3 QUICK REFERENCE CARD ".center(58) + "║")
        output.append("╠" + "═" * 58 + "╣")
        
        for category, bindings in self.essential_bindings.items():
            output.append("║ " + category.ljust(56) + " ║")
            output.append("║" + "─" * 58 + "║")
            
            for key, desc in bindings:
                key_display = key.replace('$mod', 'Super').ljust(25)
                desc_display = desc.ljust(30)
                output.append(f"║  {key_display} → {desc_display} ║")
            
            output.append("║" + " " * 58 + "║")
        
        output.append("╚" + "═" * 58 + "╝")
        output.append("\n💡 Tip: $mod = Super/Windows key")
        output.append("📖 Full help: Super+Alt+H")
        
        return '\n'.join(output)
    
    def generate_html_cheatsheet(self) -> str:
        """Generate an HTML cheat sheet with print-friendly CSS"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>i3 Cheat Sheet</title>
    <style>
        @page { size: A4; margin: 1cm; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        @media print {
            body { background: white; color: black; }
            .card { border: 1px solid #ccc !important; }
        }
        h1 {
            text-align: center;
            color: #4fc3f7;
            border-bottom: 3px solid #4fc3f7;
            padding-bottom: 10px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .card {
            background: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .card h2 {
            margin: 0 0 10px 0;
            font-size: 1.2em;
            border-bottom: 2px solid #4fc3f7;
            padding-bottom: 5px;
        }
        .binding {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #3d3d3d;
        }
        .binding:last-child { border-bottom: none; }
        .key {
            font-family: 'Consolas', 'Monaco', monospace;
            background: #1e1e1e;
            padding: 2px 6px;
            border-radius: 3px;
            border: 1px solid #4fc3f7;
            color: #4fc3f7;
            font-size: 0.9em;
        }
        .desc {
            color: #a0a0a0;
            font-size: 0.9em;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #3d3d3d;
            color: #808080;
        }
        .print-button {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 10px 20px;
            background: #4fc3f7;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        @media print {
            .print-button { display: none; }
        }
    </style>
</head>
<body>
    <button class="print-button" onclick="window.print()">🖨️ Print</button>
    <h1>🎯 i3 Window Manager - Cheat Sheet</h1>
    <div class="grid">
"""
        
        for category, bindings in self.essential_bindings.items():
            html += f"""
        <div class="card">
            <h2>{category}</h2>
"""
            for key, desc in bindings:
                key_display = key.replace('$mod', 'Super')
                html += f"""
            <div class="binding">
                <span class="key">{key_display}</span>
                <span class="desc">{desc}</span>
            </div>
"""
            html += """
        </div>
"""
        
        html += """
    </div>
    <div class="footer">
        <p>💡 <strong>$mod = Super/Windows key</strong></p>
        <p>📖 Full interactive help: <span class="key">Super+Alt+H</span></p>
        <p>Generated with i3 Help System</p>
    </div>
</body>
</html>"""
        return html
    
    def generate_markdown_cheatsheet(self) -> str:
        """Generate a Markdown cheat sheet"""
        md = ["# 🎯 i3 Window Manager - Quick Reference\n"]
        md.append("## Essential Keybindings\n")
        md.append("| Category | Key | Action |")
        md.append("|----------|-----|--------|")
        
        for category, bindings in self.essential_bindings.items():
            for i, (key, desc) in enumerate(bindings):
                cat_display = category if i == 0 else ""
                key_display = f"`{key.replace('$mod', 'Super')}`"
                md.append(f"| {cat_display} | {key_display} | {desc} |")
        
        md.append("\n---")
        md.append("\n**💡 Note:** `$mod` = Super/Windows key")
        md.append("\n**📖 Full Help:** Press `Super+Alt+H` for interactive help")
        
        return '\n'.join(md)
    
    def save_all_formats(self, output_dir: Path = None):
        """Save cheat sheet in all formats"""
        if output_dir is None:
            output_dir = Path.home() / '.config' / 'i3'
        
        # Terminal version
        terminal_content = self.generate_terminal_cheatsheet()
        with open(output_dir / 'cheatsheet.txt', 'w') as f:
            f.write(terminal_content)
        
        # HTML version
        html_content = self.generate_html_cheatsheet()
        with open(output_dir / 'cheatsheet.html', 'w') as f:
            f.write(html_content)
        
        # Markdown version
        md_content = self.generate_markdown_cheatsheet()
        with open(output_dir / 'cheatsheet.md', 'w') as f:
            f.write(md_content)
        
        print(f"✅ Cheat sheets generated in {output_dir}:")
        print(f"   • cheatsheet.txt  - Terminal version")
        print(f"   • cheatsheet.html - Printable web version")
        print(f"   • cheatsheet.md   - Markdown version")

if __name__ == "__main__":
    generator = CheatSheetGenerator()
    
    # Print to terminal
    print(generator.generate_terminal_cheatsheet())
    
    # Save all formats
    generator.save_all_formats()
