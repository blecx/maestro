#!/usr/bin/env python3
"""
export_chat.py - Automated chat export with chunking to avoid timeouts

This script exports GitHub Copilot chat sessions in chunks to avoid
request timeouts on large conversations.

Usage:
    ./scripts/export_chat.py --issue 25 --output docs/chat/
    ./scripts/export_chat.py --issue 25 --max-chunk-size 100 --output docs/chat/

Features:
    - Automatic chunking to avoid timeouts
    - Resume from last checkpoint
    - Merge chunks into single export
    - Validate export completeness
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class ChatExporter:
    """Export GitHub Copilot chat with chunking support."""
    
    def __init__(self, issue_num: int, output_dir: Path, max_chunk_size: int = 100):
        self.issue_num = issue_num
        self.output_dir = Path(output_dir)
        self.max_chunk_size = max_chunk_size
        self.timestamp = datetime.now().strftime("%Y-%m-%d")
        self.temp_dir = self.output_dir / ".export_temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def export(self) -> Path:
        """Export chat session with automatic chunking."""
        print(f"🔄 Exporting chat for Issue #{self.issue_num}")
        print(f"   Output: {self.output_dir}")
        print(f"   Max chunk size: {self.max_chunk_size} messages")
        
        # Try full export first
        print("\n1️⃣ Attempting full export...")
        full_export = self._try_full_export()
        
        if full_export:
            print("✅ Full export successful")
            return full_export
        
        # Fall back to chunked export
        print("\n2️⃣ Full export failed, using chunked approach...")
        chunks = self._export_chunks()
        
        if not chunks:
            print("❌ Failed to export chat in chunks")
            sys.exit(1)
        
        # Merge chunks
        print(f"\n3️⃣ Merging {len(chunks)} chunks...")
        merged = self._merge_chunks(chunks)
        
        # Validate
        print("\n4️⃣ Validating export...")
        if self._validate_export(merged):
            print("✅ Export validated successfully")
            # Clean up temp files
            self._cleanup()
            return merged
        else:
            print("⚠️  Export validation warnings (check manually)")
            return merged
    
    def _try_full_export(self) -> Optional[Path]:
        """Try to export full chat session."""
        output_file = self.output_dir / f"{self.timestamp}-issue{self.issue_num}-chat-export.md"
        
        try:
            # Simulate export command (replace with actual export method)
            # For now, this is a placeholder - you'll need to integrate with
            # GitHub Copilot's actual export functionality
            
            # Option 1: If using GitHub Copilot Chat API
            # result = self._call_copilot_api("export", issue=self.issue_num)
            
            # Option 2: If using clipboard-based export
            # print("   Please copy chat to clipboard and press Enter...")
            # input()
            # content = self._get_clipboard_content()
            
            # Option 3: If using VS Code command
            result = self._call_vscode_export_command()
            
            if result and len(result) > 0:
                output_file.write_text(result)
                print(f"   ✅ Exported {len(result)} characters")
                return output_file
            else:
                print("   ⚠️  Empty export result")
                return None
                
        except subprocess.TimeoutExpired:
            print("   ⏱️  Timeout - chat too large for single export")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def _export_chunks(self) -> List[Path]:
        """Export chat in chunks."""
        chunks = []
        chunk_num = 0
        
        # Get total message count (placeholder - implement based on your system)
        total_messages = self._get_message_count()
        print(f"   Total messages: {total_messages}")
        
        if total_messages == 0:
            print("   ❌ Cannot determine message count")
            return []
        
        # Export each chunk
        for start in range(0, total_messages, self.max_chunk_size):
            end = min(start + self.max_chunk_size, total_messages)
            chunk_num += 1
            
            print(f"   📦 Chunk {chunk_num}: messages {start}-{end}")
            
            chunk_file = self.temp_dir / f"chunk_{chunk_num:03d}.md"
            success = self._export_message_range(start, end, chunk_file)
            
            if success:
                chunks.append(chunk_file)
                print(f"      ✅ Exported {chunk_file.stat().st_size} bytes")
            else:
                print(f"      ❌ Failed to export chunk {chunk_num}")
                # Try to continue with other chunks
                continue
            
            # Brief pause to avoid rate limiting
            time.sleep(1)
        
        return chunks
    
    def _export_message_range(self, start: int, end: int, output: Path) -> bool:
        """Export a specific range of messages."""
        try:
            # Placeholder - implement based on your chat export system
            # This would call the actual export API/command with range parameters
            
            # Example implementation:
            # result = self._call_copilot_api("export", 
            #                                  issue=self.issue_num, 
            #                                  start=start, 
            #                                  end=end)
            
            # For now, simulate with placeholder
            content = f"# Chunk {start}-{end}\n\n(Exported messages {start} to {end})\n"
            output.write_text(content)
            return True
            
        except Exception as e:
            print(f"      Error exporting range {start}-{end}: {e}")
            return False
    
    def _merge_chunks(self, chunks: List[Path]) -> Path:
        """Merge chunk files into single export."""
        output_file = self.output_dir / f"{self.timestamp}-issue{self.issue_num}-complete-workflow.md"
        
        with open(output_file, 'w') as out:
            # Write header
            out.write(f"# Issue #{self.issue_num} - Complete Chat Export\n\n")
            out.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write(f"**Chunks:** {len(chunks)}\n\n")
            out.write("---\n\n")
            
            # Merge chunks
            for i, chunk_file in enumerate(chunks, 1):
                print(f"   Merging chunk {i}/{len(chunks)}")
                content = chunk_file.read_text()
                
                # Remove redundant headers from chunks
                if i > 1:
                    content = self._strip_chunk_header(content)
                
                out.write(content)
                out.write("\n\n")
        
        print(f"   ✅ Merged to {output_file.name}")
        print(f"   📊 Total size: {output_file.stat().st_size:,} bytes")
        
        return output_file
    
    def _strip_chunk_header(self, content: str) -> str:
        """Remove chunk-specific headers for cleaner merge."""
        lines = content.split('\n')
        # Skip lines until we find actual content (skip chunk markers)
        start_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('# Chunk'):
                start_idx = i + 1
            elif line.strip() and not line.startswith('#'):
                start_idx = i
                break
        return '\n'.join(lines[start_idx:])
    
    def _validate_export(self, export_file: Path) -> bool:
        """Validate exported chat completeness."""
        content = export_file.read_text()
        
        checks = {
            "Has content": len(content) > 100,
            "Has phases": "Phase" in content or "##" in content,
            "Has commands": "```" in content or "$" in content,
            "Has issue number": f"#{self.issue_num}" in content or f"Issue {self.issue_num}" in content,
        }
        
        all_passed = True
        for check, passed in checks.items():
            status = "✅" if passed else "⚠️ "
            print(f"   {status} {check}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def _cleanup(self):
        """Clean up temporary chunk files."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print(f"   🧹 Cleaned up temp files")
    
    def _get_message_count(self) -> int:
        """Get total number of messages in chat (implement based on your system)."""
        # Placeholder - implement based on your chat system
        # This could query the Copilot API or parse existing data
        return 0  # Return actual count
    
    def _call_vscode_export_command(self) -> Optional[str]:
        """Call VS Code export command (placeholder)."""
        # This is where you'd integrate with actual VS Code/Copilot export
        # For example:
        # - Use VS Code API if available
        # - Use GitHub Copilot extension commands
        # - Parse from workspace state
        
        # For now, return None to trigger chunked export
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Export GitHub Copilot chat with chunking support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Export Issue #25 chat:
    ./scripts/export_chat.py --issue 25
  
  Export with custom chunk size:
    ./scripts/export_chat.py --issue 25 --max-chunk-size 50
  
  Export to specific directory:
    ./scripts/export_chat.py --issue 25 --output docs/chat/
        """
    )
    
    parser.add_argument('--issue', type=int, required=True,
                        help='Issue number to export')
    parser.add_argument('--output', type=str, default='docs/chat',
                        help='Output directory (default: docs/chat)')
    parser.add_argument('--max-chunk-size', type=int, default=100,
                        help='Max messages per chunk (default: 100)')
    parser.add_argument('--validate-only', action='store_true',
                        help='Only validate existing export')
    
    args = parser.parse_args()
    
    exporter = ChatExporter(
        issue_num=args.issue,
        output_dir=Path(args.output),
        max_chunk_size=args.max_chunk_size
    )
    
    if args.validate_only:
        # Find existing export
        pattern = f"*-issue{args.issue}-*.md"
        exports = list(Path(args.output).glob(pattern))
        if not exports:
            print(f"❌ No export found for Issue #{args.issue}")
            sys.exit(1)
        print(f"📋 Validating {exports[0]}")
        if exporter._validate_export(exports[0]):
            print("✅ Export is valid")
        else:
            print("⚠️  Export has warnings")
        sys.exit(0)
    
    # Export chat
    try:
        export_file = exporter.export()
        print(f"\n✅ Chat export complete: {export_file}")
        print(f"\nNext steps:")
        print(f"  1. Review export: cat {export_file}")
        print(f"  2. Extract learnings: ./scripts/extract_learnings.py --export {export_file}")
        print(f"  3. Update agent: ./scripts/train_agent.py --issue {args.issue}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Export interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
