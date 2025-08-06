#!/usr/bin/env python3
"""
Export Engine for i3 Keybinding Documentation

Supports multiple export formats:
- HTML: Rich web format with CSS styling and interactive features
- PDF: Print-ready format with proper typography (requires weasyprint)
- Markdown: Documentation format for GitHub/wikis
- JSON: Structured data format for programmatic use
- Plain Text: Simple format for sharing and backup
- CSV: Spreadsheet format for analysis

Features:
- Customizable templates and styling
- Category-based organization
- Usage statistics integration
- Responsive and print-friendly layouts
"""

import json
import csv
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
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
    theme: str = "default"  # default, dark, minimal, print
    custom_title: str = ""
    custom_description: str = ""

class ExportEngine:
    """Handles exporting keybinding data to various formats"""
    
    def __init__(self):
        self.supported_formats = {
            'html': self.export_html,
            'pdf': self.export_pdf,
            'markdown': self.export_markdown,
            'md': self.export_markdown,
            'json': self.export_json,
            'txt': self.export_text,
            'text': self.export_text,
            'csv': self.export_csv
        }
        
        # Check for optional dependencies
        self.weasyprint_available = self._check_weasyprint()
    
    def _check_weasyprint(self) -> bool:
        """Check if weasyprint is available for PDF export"""
        try:
            import weasyprint
            return True
        except ImportError:
            return False
    
    def export(self, bindings: List[Dict], analytics: Dict, options: ExportOptions) -> bool:
        """Export bindings to specified format"""
        format_key = options.format.lower()
        
        if format_key not in self.supported_formats:
            raise ValueError(f"Unsupported format: {options.format}")
        
        # Create output directory if needed
        output_path = Path(options.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            return self.supported_formats[format_key](bindings, analytics, options)
        except Exception as e:
            print(f"Export failed: {str(e)}")
            return False
    
    def export_html(self, bindings: List[Dict], analytics: Dict, options: ExportOptions) -> bool:
        """Export to HTML format with CSS styling"""
        
        # Sort bindings based on options
        sorted_bindings = self._sort_bindings(bindings, analytics, options.sort_by)
        
        # Group by categories
        categories = self._group_by_categories(sorted_bindings) if options.include_categories else {"All Bindings": sorted_bindings}
        
        # Generate HTML content
        html_content = self._generate_html(categories, analytics, options)
        
        # Write to file
        try:
            with open(options.output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"Failed to write HTML file: {e}")
            return False
    
    def export_pdf(self, bindings: List[Dict], analytics: Dict, options: ExportOptions) -> bool:
        """Export to PDF format"""
        if not self.weasyprint_available:
            print("PDF export requires weasyprint: pip install weasyprint")
            return False
        
        try:
            import weasyprint
            
            # Generate HTML first
            temp_options = ExportOptions(
                format="html",
                output_path="temp.html",
                include_categories=options.include_categories,
                include_subcategories=options.include_subcategories,
                include_usage_stats=options.include_usage_stats,
                sort_by=options.sort_by,
                theme="print",  # Use print theme for PDF
                custom_title=options.custom_title,
                custom_description=options.custom_description
            )
            
            sorted_bindings = self._sort_bindings(bindings, analytics, options.sort_by)
            categories = self._group_by_categories(sorted_bindings) if options.include_categories else {"All Bindings": sorted_bindings}
            html_content = self._generate_html(categories, analytics, temp_options)
            
            # Convert HTML to PDF
            weasyprint.HTML(string=html_content).write_pdf(options.output_path)
            return True
            
        except Exception as e:
            print(f"PDF export failed: {e}")
            return False
    
    def export_markdown(self, bindings: List[Dict], analytics: Dict, options: ExportOptions) -> bool:
        """Export to Markdown format"""
        sorted_bindings = self._sort_bindings(bindings, analytics, options.sort_by)
        categories = self._group_by_categories(sorted_bindings) if options.include_categories else {"All Bindings": sorted_bindings}
        
        md_content = self._generate_markdown(categories, analytics, options)
        
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
        
        # Create structured JSON output
        export_data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "total_bindings": len(sorted_bindings),
                "format_version": "1.0",
                "title": options.custom_title or "i3 Keybindings Export",
                "description": options.custom_description or "Generated by i3-help utility"
            },
            "categories": {},
            "bindings": []
        }
        
        if options.include_categories:
            categories = self._group_by_categories(sorted_bindings)
            for cat_name, cat_bindings in categories.items():
                export_data["categories"][cat_name] = {
                    "count": len(cat_bindings),
                    "bindings": [b['key'] for b in cat_bindings]
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
            
            if options.include_search_terms:
                binding_data["search_terms"] = binding.get('search_text', '').split()
            
            export_data["bindings"].append(binding_data)
        
        # Add analytics if requested
        if options.include_usage_stats:
            export_data["analytics"] = {
                "most_used": analytics.get('popular_bindings', [])[:10],
                "total_usage": sum(analytics.get('binding_usage', {}).values()),
                "last_updated": analytics.get('last_updated')
            }
        
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
        
        text_content = self._generate_text(categories, analytics, options)
        
        try:
            with open(options.output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            return True
        except Exception as e:
            print(f"Failed to write text file: {e}")
            return False
    
    def export_csv(self, bindings: List[Dict], analytics: Dict, options: ExportOptions) -> bool:
        """Export to CSV format for spreadsheet analysis"""
        sorted_bindings = self._sort_bindings(bindings, analytics, options.sort_by)
        
        try:
            with open(options.output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['key', 'description', 'category', 'subcategory']
                
                if options.include_commands:
                    fieldnames.append('command')
                
                if options.include_usage_stats:
                    fieldnames.append('usage_count')
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for binding in sorted_bindings:
                    row = {
                        'key': binding['key'],
                        'description': binding['description'],
                        'category': binding.get('category', ''),
                        'subcategory': binding.get('subcategory', '')
                    }
                    
                    if options.include_commands:
                        row['command'] = binding['command']
                    
                    if options.include_usage_stats:
                        key_id = f"{binding['key']}:{binding['description']}"
                        row['usage_count'] = analytics.get('binding_usage', {}).get(key_id, 0)
                    
                    writer.writerow(row)
            
            return True
        except Exception as e:
            print(f"Failed to write CSV file: {e}")
            return False
    
    def _sort_bindings(self, bindings: List[Dict], analytics: Dict, sort_by: str) -> List[Dict]:
        """Sort bindings based on specified criteria"""
        if sort_by == "alphabetical":
            return sorted(bindings, key=lambda x: x['description'].lower())
        elif sort_by == "usage":
            def usage_score(binding):
                key_id = f"{binding['key']}:{binding['description']}"
                return analytics.get('binding_usage', {}).get(key_id, 0)
            return sorted(bindings, key=usage_score, reverse=True)
        else:  # category
            return sorted(bindings, key=lambda x: (x.get('category', ''), x.get('subcategory', ''), x['description']))
    
    def _group_by_categories(self, bindings: List[Dict]) -> Dict[str, List[Dict]]:
        """Group bindings by categories"""
        categories = {}
        
        for binding in bindings:
            category = binding.get('category', '🔧 Uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(binding)
        
        return categories
    
    def _generate_html(self, categories: Dict[str, List[Dict]], analytics: Dict, options: ExportOptions) -> str:
        """Generate HTML content"""
        
        title = options.custom_title or "i3 Keybindings Reference"
        description = options.custom_description or "Complete reference guide for i3 window manager keybindings"
        
        # CSS styles based on theme
        css_styles = self._get_css_styles(options.theme)
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css_styles}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <p class="description">{description}</p>
        <div class="metadata">
            <span>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            <span>Total bindings: {sum(len(bindings) for bindings in categories.values())}</span>
        </div>
    </header>
    
    <div class="search-container">
        <input type="text" id="searchInput" placeholder="Search keybindings...">
    </div>
    
    <nav class="table-of-contents">
        <h2>Table of Contents</h2>
        <ul>
"""
        
        # Table of contents
        for category_name, bindings in categories.items():
            if bindings:
                html += f'            <li><a href="#{self._make_anchor(category_name)}">{category_name} ({len(bindings)})</a></li>\n'
        
        html += """        </ul>
    </nav>
    
    <main>
"""
        
        # Categories and bindings
        for category_name, bindings in categories.items():
            if not bindings:
                continue
                
            html += f"""        <section class="category" id="{self._make_anchor(category_name)}">
            <h2>{category_name}</h2>
"""
            
            if options.include_subcategories:
                # Group by subcategories
                subcategories = {}
                for binding in bindings:
                    subcat = binding.get('subcategory', 'General')
                    if subcat not in subcategories:
                        subcategories[subcat] = []
                    subcategories[subcat].append(binding)
                
                for subcat_name, subcat_bindings in subcategories.items():
                    if subcat_bindings:
                        html += f"""            <div class="subcategory">
                <h3>{subcat_name}</h3>
                <div class="bindings-grid">
"""
                        for binding in subcat_bindings:
                            usage_count = ""
                            if options.include_usage_stats:
                                key_id = f"{binding['key']}:{binding['description']}"
                                count = analytics.get('binding_usage', {}).get(key_id, 0)
                                if count > 0:
                                    usage_count = f'<span class="usage-count">{count} uses</span>'
                            
                            html += f"""                    <div class="binding-card">
                        <div class="key-combo">{binding['key']}</div>
                        <div class="description">{binding['description']}</div>
                        {f'<div class="command">{binding["command"]}</div>' if options.include_commands else ''}
                        {usage_count}
                    </div>
"""
                        html += """                </div>
            </div>
"""
            else:
                # Flat list without subcategories
                html += """            <div class="bindings-grid">
"""
                for binding in bindings:
                    usage_count = ""
                    if options.include_usage_stats:
                        key_id = f"{binding['key']}:{binding['description']}"
                        count = analytics.get('binding_usage', {}).get(key_id, 0)
                        if count > 0:
                            usage_count = f'<span class="usage-count">{count} uses</span>'
                    
                    html += f"""                <div class="binding-card">
                    <div class="key-combo">{binding['key']}</div>
                    <div class="description">{binding['description']}</div>
                    {f'<div class="command">{binding["command"]}</div>' if options.include_commands else ''}
                    {usage_count}
                </div>
"""
                html += """            </div>
"""
            html += """        </section>
"""
        
        # Analytics section
        if options.include_usage_stats and analytics.get('binding_usage'):
            popular_bindings = sorted(analytics['binding_usage'].items(), key=lambda x: x[1], reverse=True)[:10]
            html += """        <section class="analytics">
            <h2>📊 Usage Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Most Used Bindings</h3>
                    <ol class="popular-list">
"""
            for key_desc, count in popular_bindings:
                key_part = key_desc.split(':')[0]
                desc_part = ':'.join(key_desc.split(':')[1:])
                html += f'                        <li><span class="key">{key_part}</span> - {desc_part} <span class="count">({count} uses)</span></li>\n'
            
            html += """                    </ol>
                </div>
            </div>
        </section>
"""
        
        html += """    </main>
    
    <script>
        // Search functionality
        document.getElementById('searchInput').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const bindingCards = document.querySelectorAll('.binding-card');
            
            bindingCards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_markdown(self, categories: Dict[str, List[Dict]], analytics: Dict, options: ExportOptions) -> str:
        """Generate Markdown content"""
        
        title = options.custom_title or "i3 Keybindings Reference"
        description = options.custom_description or "Complete reference guide for i3 window manager keybindings"
        
        md = f"""# {title}

{description}

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total bindings:** {sum(len(bindings) for bindings in categories.values())}

## Table of Contents

"""
        
        # Table of contents
        for category_name, bindings in categories.items():
            if bindings:
                anchor = self._make_anchor(category_name)
                md += f"- [{category_name}](#{anchor}) ({len(bindings)} bindings)\n"
        
        md += "\n---\n\n"
        
        # Categories and bindings
        for category_name, bindings in categories.items():
            if not bindings:
                continue
            
            md += f"## {category_name}\n\n"
            
            if options.include_subcategories:
                # Group by subcategories
                subcategories = {}
                for binding in bindings:
                    subcat = binding.get('subcategory', 'General')
                    if subcat not in subcategories:
                        subcategories[subcat] = []
                    subcategories[subcat].append(binding)
                
                for subcat_name, subcat_bindings in subcategories.items():
                    if subcat_bindings:
                        md += f"### {subcat_name}\n\n"
                        md += "| Key Combination | Description |"
                        if options.include_commands:
                            md += " Command |"
                        if options.include_usage_stats:
                            md += " Usage Count |"
                        md += "\n"
                        
                        md += "|---|---|"
                        if options.include_commands:
                            md += "---|"
                        if options.include_usage_stats:
                            md += "---|"
                        md += "\n"
                        
                        for binding in subcat_bindings:
                            md += f"| `{binding['key']}` | {binding['description']} |"
                            
                            if options.include_commands:
                                md += f" `{binding['command']}` |"
                            
                            if options.include_usage_stats:
                                key_id = f"{binding['key']}:{binding['description']}"
                                count = analytics.get('binding_usage', {}).get(key_id, 0)
                                md += f" {count} |"
                            
                            md += "\n"
                        
                        md += "\n"
            else:
                # Flat table
                md += "| Key Combination | Description |"
                if options.include_commands:
                    md += " Command |"
                if options.include_usage_stats:
                    md += " Usage Count |"
                md += "\n"
                
                md += "|---|---|"
                if options.include_commands:
                    md += "---|"
                if options.include_usage_stats:
                    md += "---|"
                md += "\n"
                
                for binding in bindings:
                    md += f"| `{binding['key']}` | {binding['description']} |"
                    
                    if options.include_commands:
                        md += f" `{binding['command']}` |"
                    
                    if options.include_usage_stats:
                        key_id = f"{binding['key']}:{binding['description']}"
                        count = analytics.get('binding_usage', {}).get(key_id, 0)
                        md += f" {count} |"
                    
                    md += "\n"
                
                md += "\n"
        
        # Usage statistics
        if options.include_usage_stats and analytics.get('binding_usage'):
            md += "## 📊 Usage Statistics\n\n"
            
            popular_bindings = sorted(analytics['binding_usage'].items(), key=lambda x: x[1], reverse=True)[:10]
            md += "### Most Used Bindings\n\n"
            
            for i, (key_desc, count) in enumerate(popular_bindings, 1):
                key_part = key_desc.split(':')[0]
                desc_part = ':'.join(key_desc.split(':')[1:])
                md += f"{i}. `{key_part}` - {desc_part} ({count} uses)\n"
            
            md += "\n"
        
        return md
    
    def _generate_text(self, categories: Dict[str, List[Dict]], analytics: Dict, options: ExportOptions) -> str:
        """Generate plain text content"""
        
        title = options.custom_title or "i3 KEYBINDINGS REFERENCE"
        description = options.custom_description or "Complete reference guide for i3 window manager keybindings"
        
        text = f"""{title}
{'=' * len(title)}

{description}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total bindings: {sum(len(bindings) for bindings in categories.values())}

{'=' * 80}

"""
        
        # Categories and bindings
        for category_name, bindings in categories.items():
            if not bindings:
                continue
            
            text += f"\n{category_name}\n"
            text += "-" * len(category_name) + "\n\n"
            
            if options.include_subcategories:
                # Group by subcategories
                subcategories = {}
                for binding in bindings:
                    subcat = binding.get('subcategory', 'General')
                    if subcat not in subcategories:
                        subcategories[subcat] = []
                    subcategories[subcat].append(binding)
                
                for subcat_name, subcat_bindings in subcategories.items():
                    if subcat_bindings:
                        text += f"\n  {subcat_name}:\n"
                        
                        for binding in subcat_bindings:
                            key_part = f"[{binding['key']}]".ljust(20)
                            text += f"    {key_part} {binding['description']}\n"
                            
                            if options.include_commands:
                                text += f"                         Command: {binding['command']}\n"
                            
                            if options.include_usage_stats:
                                key_id = f"{binding['key']}:{binding['description']}"
                                count = analytics.get('binding_usage', {}).get(key_id, 0)
                                if count > 0:
                                    text += f"                         Usage: {count} times\n"
                        
                        text += "\n"
            else:
                # Flat list
                for binding in bindings:
                    key_part = f"[{binding['key']}]".ljust(20)
                    text += f"  {key_part} {binding['description']}\n"
                    
                    if options.include_commands:
                        text += f"                       Command: {binding['command']}\n"
                    
                    if options.include_usage_stats:
                        key_id = f"{binding['key']}:{binding['description']}"
                        count = analytics.get('binding_usage', {}).get(key_id, 0)
                        if count > 0:
                            text += f"                       Usage: {count} times\n"
                
                text += "\n"
        
        # Usage statistics
        if options.include_usage_stats and analytics.get('binding_usage'):
            text += "\nUSAGE STATISTICS\n"
            text += "================\n\n"
            
            popular_bindings = sorted(analytics['binding_usage'].items(), key=lambda x: x[1], reverse=True)[:10]
            text += "Most Used Bindings:\n\n"
            
            for i, (key_desc, count) in enumerate(popular_bindings, 1):
                key_part = key_desc.split(':')[0]
                desc_part = ':'.join(key_desc.split(':')[1:])
                text += f"  {i:2d}. [{key_part}] - {desc_part} ({count} uses)\n"
            
            text += "\n"
        
        return text
    
    def _get_css_styles(self, theme: str) -> str:
        """Get CSS styles for different themes"""
        
        base_styles = """
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--border-color);
        }
        
        h1 {
            color: var(--primary-color);
            margin-bottom: 0.5rem;
            font-size: 2.5rem;
        }
        
        .description {
            font-size: 1.1rem;
            color: var(--text-muted);
            margin-bottom: 1rem;
        }
        
        .metadata {
            font-size: 0.9rem;
            color: var(--text-muted);
        }
        
        .metadata span {
            margin: 0 1rem;
        }
        
        .search-container {
            margin-bottom: 2rem;
            text-align: center;
        }
        
        #searchInput {
            width: 300px;
            padding: 0.7rem;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 1rem;
            background: var(--input-bg);
            color: var(--text-color);
        }
        
        .table-of-contents {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
        }
        
        .table-of-contents ul {
            list-style: none;
            columns: 2;
        }
        
        .table-of-contents a {
            color: var(--link-color);
            text-decoration: none;
            padding: 0.2rem 0;
            display: block;
        }
        
        .table-of-contents a:hover {
            color: var(--primary-color);
        }
        
        .category {
            margin-bottom: 3rem;
        }
        
        .category h2 {
            color: var(--primary-color);
            font-size: 1.8rem;
            margin-bottom: 1rem;
            padding: 0.5rem 0;
            border-bottom: 2px solid var(--primary-color);
        }
        
        .subcategory {
            margin-bottom: 2rem;
        }
        
        .subcategory h3 {
            color: var(--secondary-color);
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }
        
        .bindings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .binding-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .binding-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: var(--primary-color);
        }
        
        .key-combo {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-weight: bold;
            color: var(--key-color);
            background: var(--key-bg);
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 0.5rem;
            border: 1px solid var(--key-border);
        }
        
        .description {
            font-weight: 500;
            color: var(--text-color);
            margin-bottom: 0.3rem;
        }
        
        .command {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.85rem;
            color: var(--text-muted);
            background: var(--code-bg);
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            margin-top: 0.3rem;
        }
        
        .usage-count {
            font-size: 0.8rem;
            color: var(--accent-color);
            font-weight: 500;
            float: right;
        }
        
        .analytics {
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            margin-top: 3rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .stat-card {
            background: var(--bg-color);
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }
        
        .popular-list {
            list-style: none;
        }
        
        .popular-list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
        }
        
        .popular-list .key {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-weight: bold;
            color: var(--key-color);
        }
        
        .popular-list .count {
            color: var(--accent-color);
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            .bindings-grid {
                grid-template-columns: 1fr;
            }
            
            .table-of-contents ul {
                columns: 1;
            }
        }
        
        @media print {
            body {
                font-size: 12pt;
                color: black;
                background: white;
            }
            
            .search-container {
                display: none;
            }
            
            .binding-card {
                break-inside: avoid;
                border: 1px solid #ddd;
                margin-bottom: 0.5rem;
            }
            
            .table-of-contents {
                break-after: page;
            }
        }
"""
        
        theme_vars = {
            'default': """
        :root {
            --bg-color: #ffffff;
            --text-color: #333333;
            --text-muted: #666666;
            --primary-color: #007acc;
            --secondary-color: #5a5a5a;
            --accent-color: #28a745;
            --link-color: #007acc;
            --border-color: #e1e5e9;
            --card-bg: #f8f9fa;
            --input-bg: #ffffff;
            --key-color: #495057;
            --key-bg: #e9ecef;
            --key-border: #ced4da;
            --code-bg: #f1f3f4;
        }
            """,
            'dark': """
        :root {
            --bg-color: #1a1a1a;
            --text-color: #e1e1e1;
            --text-muted: #b0b0b0;
            --primary-color: #4da6ff;
            --secondary-color: #a0a0a0;
            --accent-color: #40c463;
            --link-color: #4da6ff;
            --border-color: #3a3a3a;
            --card-bg: #2d2d2d;
            --input-bg: #2d2d2d;
            --key-color: #ffffff;
            --key-bg: #404040;
            --key-border: #555555;
            --code-bg: #333333;
        }
            """,
            'minimal': """
        :root {
            --bg-color: #fefefe;
            --text-color: #2c2c2c;
            --text-muted: #757575;
            --primary-color: #000000;
            --secondary-color: #4a4a4a;
            --accent-color: #666666;
            --link-color: #000000;
            --border-color: #e0e0e0;
            --card-bg: #ffffff;
            --input-bg: #ffffff;
            --key-color: #000000;
            --key-bg: #f5f5f5;
            --key-border: #d0d0d0;
            --code-bg: #f8f8f8;
        }
            """,
            'print': """
        :root {
            --bg-color: #ffffff;
            --text-color: #000000;
            --text-muted: #444444;
            --primary-color: #000000;
            --secondary-color: #333333;
            --accent-color: #000000;
            --link-color: #000000;
            --border-color: #cccccc;
            --card-bg: #ffffff;
            --input-bg: #ffffff;
            --key-color: #000000;
            --key-bg: #f0f0f0;
            --key-border: #999999;
            --code-bg: #f5f5f5;
        }
            """
        }
        
        return theme_vars.get(theme, theme_vars['default']) + base_styles
    
    def _make_anchor(self, text: str) -> str:
        """Create URL-friendly anchor from text"""
        return text.lower().replace(' ', '-').replace('&', 'and').replace('/', '-').replace('🚀', '').replace('🖥️', '').replace('🪟', '').replace('📷', '').replace('🔊', '').replace('💡', '').replace('📐', '').replace('⚙️', '').replace('🔧', '').strip('-')

def demo():
    """Demo the export engine"""
    
    # Sample bindings data
    sample_bindings = [
        {
            'key': 'Super+Return',
            'command': 'exec warp-terminal',
            'description': 'Open terminal',
            'category': '🚀 Apps & Launch',
            'subcategory': 'Applications',
            'line': 1
        },
        {
            'key': 'Super+d',
            'command': 'exec rofi -show drun',
            'description': 'Application launcher',
            'category': '🚀 Apps & Launch',
            'subcategory': 'Launchers',
            'line': 2
        },
        {
            'key': 'Print',
            'command': 'exec flameshot gui',
            'description': 'Take screenshot',
            'category': '📷 Screenshots',
            'subcategory': 'Capture',
            'line': 3
        }
    ]
    
    # Sample analytics
    sample_analytics = {
        'binding_usage': {
            'Super+Return:Open terminal': 15,
            'Super+d:Application launcher': 8,
            'Print:Take screenshot': 12
        },
        'last_updated': 1234567890
    }
    
    engine = ExportEngine()
    
    # Test HTML export
    html_options = ExportOptions(
        format="html",
        output_path="/tmp/i3-keybindings.html",
        include_categories=True,
        include_subcategories=True,
        include_usage_stats=True,
        custom_title="Demo i3 Keybindings"
    )
    
    success = engine.export(sample_bindings, sample_analytics, html_options)
    print(f"HTML export: {'✓ Success' if success else '✗ Failed'}")
    
    # Test Markdown export
    md_options = ExportOptions(
        format="markdown",
        output_path="/tmp/i3-keybindings.md"
    )
    
    success = engine.export(sample_bindings, sample_analytics, md_options)
    print(f"Markdown export: {'✓ Success' if success else '✗ Failed'}")
    
    # Test JSON export
    json_options = ExportOptions(
        format="json",
        output_path="/tmp/i3-keybindings.json"
    )
    
    success = engine.export(sample_bindings, sample_analytics, json_options)
    print(f"JSON export: {'✓ Success' if success else '✗ Failed'}")
    
    print("\nDemo exports saved to /tmp/")

if __name__ == '__main__':
    demo()
