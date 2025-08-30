#!/usr/bin/env python3
"""
Basic Export Engine for i3 Keybinding Documentation

This is a simplified version of the export engine that provides
core functionality for exporting keybindings to various formats.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ExportOptions:
    """Configuration options for exports"""
    format: str
    output_path: str
    include_categories: bool = True
    include_subcategories: bool = True
    include_usage_stats: bool = True
    include_search_terms: bool = False
    include_commands: bool = True
    include_descriptions: bool = True
    sort_by: str = "category"  # category, alphabetical, usage
    theme: str = "default"
    custom_title: str = ""
    custom_description: str = ""

class ExportEngine:
    """Handles exporting keybinding data to various formats"""
    
    def __init__(self):
        self.supported_formats = {
            'html': self.export_html,
            'markdown': self.export_markdown,
            'md': self.export_markdown,
            'json': self.export_json,
            'txt': self.export_text,
            'text': self.export_text,
        }
    
    def export(self, bindings: List[Dict], analytics: Dict, options: ExportOptions) -> bool:
        """Export bindings to specified format"""
        format_key = options.format.lower()
        
        if format_key not in self.supported_formats:
            print(f"Unsupported format: {options.format}")
            return False
        
        # Create output directory if needed
        output_path = Path(options.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            return self.supported_formats[format_key](bindings, analytics, options)
        except Exception as e:
            print(f"Export failed: {str(e)}")
            return False
    
    def _sort_bindings(self, bindings: List[Dict], analytics: Dict, sort_by: str) -> List[Dict]:
        """Sort bindings based on criteria"""
        if sort_by == "alphabetical":
            return sorted(bindings, key=lambda x: x['description'])
        elif sort_by == "usage":
            def get_usage(binding):
                key_id = f"{binding['key']}:{binding['description']}"
                return analytics.get('binding_usage', {}).get(key_id, 0)
            return sorted(bindings, key=get_usage, reverse=True)
        else:  # category
            return sorted(bindings, key=lambda x: (x.get('category', ''), x.get('subcategory', ''), x['description']))
    
    def _group_by_categories(self, bindings: List[Dict]) -> Dict[str, List[Dict]]:
        """Group bindings by category"""
        categories = {}
        for binding in bindings:
            cat = binding.get('category', 'Uncategorized')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(binding)
        return categories
    
    def export_html(self, bindings: List[Dict], analytics: Dict, options: ExportOptions) -> bool:
        """Export to HTML format"""
        sorted_bindings = self._sort_bindings(bindings, analytics, options.sort_by)
        categories = self._group_by_categories(sorted_bindings) if options.include_categories else {"All Bindings": sorted_bindings}
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{options.custom_title or 'i3 Keybindings'}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .binding {{ margin: 10px 0; padding: 10px; border-left: 3px solid #4CAF50; background: #f9f9f9; }}
        .key {{ font-family: monospace; background: #eee; padding: 2px 6px; border-radius: 3px; }}
        .description {{ font-weight: bold; }}
        .command {{ font-family: monospace; color: #666; font-size: 0.9em; }}
        .stats {{ font-size: 0.8em; color: #888; }}
    </style>
</head>
<body>
    <h1>{options.custom_title or 'i3 Keybindings Reference'}</h1>
    <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
"""

        for category, bindings_list in categories.items():
            html_content += f"<h2>{category}</h2>\n"
            for binding in bindings_list:
                usage_count = 0
                if options.include_usage_stats:
                    key_id = f"{binding['key']}:{binding['description']}"
                    usage_count = analytics.get('binding_usage', {}).get(key_id, 0)
                
                html_content += f"""<div class="binding">
    <div class="description">{binding['description']}</div>
    <div>Key: <span class="key">{binding['key']}</span></div>"""
                
                if options.include_commands:
                    html_content += f'<div class="command">Command: {binding["command"]}</div>'
                
                if options.include_usage_stats and usage_count > 0:
                    html_content += f'<div class="stats">Used {usage_count} times</div>'
                
                html_content += "</div>\n"

        html_content += """
</body>
</html>"""
        
        try:
            with open(options.output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"Failed to write HTML file: {e}")
            return False
    
    def export_markdown(self, bindings: List[Dict], analytics: Dict, options: ExportOptions) -> bool:
        """Export to Markdown format"""
        sorted_bindings = self._sort_bindings(bindings, analytics, options.sort_by)
        categories = self._group_by_categories(sorted_bindings) if options.include_categories else {"All Bindings": sorted_bindings}
        
        md_content = f"# {options.custom_title or 'i3 Keybindings Reference'}\n\n"
        md_content += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        for category, bindings_list in categories.items():
            md_content += f"## {category}\n\n"
            for binding in bindings_list:
                usage_count = 0
                if options.include_usage_stats:
                    key_id = f"{binding['key']}:{binding['description']}"
                    usage_count = analytics.get('binding_usage', {}).get(key_id, 0)
                
                md_content += f"### {binding['description']}\n\n"
                md_content += f"**Key:** `{binding['key']}`\n\n"
                
                if options.include_commands:
                    md_content += f"**Command:** `{binding['command']}`\n\n"
                
                if options.include_usage_stats and usage_count > 0:
                    md_content += f"*Used {usage_count} times*\n\n"
                
                md_content += "---\n\n"
        
        try:
            with open(options.output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            return True
        except Exception as e:
            print(f"Failed to write Markdown file: {e}")
            return False
    
    def export_json(self, bindings: List[Dict], analytics: Dict, options: ExportOptions) -> bool:
        """Export to JSON format"""
        sorted_bindings = self._sort_bindings(bindings, analytics, options.sort_by)
        
        export_data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "total_bindings": len(sorted_bindings),
                "format_version": "1.0",
                "title": options.custom_title or "i3 Keybindings Export",
                "description": options.custom_description or "Generated by i3-help utility"
            },
            "bindings": []
        }
        
        # Add binding data
        for binding in sorted_bindings:
            binding_data = {
                "key": binding['key'],
                "description": binding['description'],
                "category": binding.get('category', ''),
                "subcategory": binding.get('subcategory', '')
            }
            
            if options.include_commands:
                binding_data["command"] = binding['command']
            
            if options.include_usage_stats:
                key_id = f"{binding['key']}:{binding['description']}"
                binding_data["usage_count"] = analytics.get('binding_usage', {}).get(key_id, 0)
            
            export_data["bindings"].append(binding_data)
        
        try:
            with open(options.output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to write JSON file: {e}")
            return False
    
    def export_text(self, bindings: List[Dict], analytics: Dict, options: ExportOptions) -> bool:
        """Export to plain text format"""
        sorted_bindings = self._sort_bindings(bindings, analytics, options.sort_by)
        categories = self._group_by_categories(sorted_bindings) if options.include_categories else {"All Bindings": sorted_bindings}
        
        text_content = f"{options.custom_title or 'i3 Keybindings Reference'}\n"
        text_content += "=" * len(text_content.strip()) + "\n\n"
        text_content += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for category, bindings_list in categories.items():
            text_content += f"{category}\n"
            text_content += "-" * len(category) + "\n\n"
            
            for binding in bindings_list:
                usage_count = 0
                if options.include_usage_stats:
                    key_id = f"{binding['key']}:{binding['description']}"
                    usage_count = analytics.get('binding_usage', {}).get(key_id, 0)
                
                text_content += f"  {binding['description']}\n"
                text_content += f"    Key: {binding['key']}\n"
                
                if options.include_commands:
                    text_content += f"    Command: {binding['command']}\n"
                
                if options.include_usage_stats and usage_count > 0:
                    text_content += f"    Used {usage_count} times\n"
                
                text_content += "\n"
            
            text_content += "\n"
        
        try:
            with open(options.output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            return True
        except Exception as e:
            print(f"Failed to write text file: {e}")
            return False
