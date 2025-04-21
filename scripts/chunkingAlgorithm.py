

import uuid
from typing import List, Dict, Any

class HierarchicalChunker:
    def __init__(self, max_tokens=500, model=None):
        self.max_tokens = max_tokens
        self.model = model

    def chunk(self, structured_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        current_chunk = []
        current_tokens = 0

        def add_chunk():
            nonlocal current_chunk, current_tokens
            if current_chunk:
                chunks.append(self._create_chunk(current_chunk))
                current_chunk = []
                current_tokens = 0

        for item in structured_data:
            item_text = self._item_text(item)
            tokens = self._count_tokens(item_text)

            if tokens > self.max_tokens:
                # Fallback: Break large item into smaller parts line-by-line
                if item["type"] == "Paragraph" and "text" in item:
                    lines = item["text"].split(". ")
                    sub_chunk = []
                    sub_tokens = 0
                    for line in lines:
                        line_tokens = self._count_tokens(line)
                        if sub_tokens + line_tokens > self.max_tokens:
                            if sub_chunk:
                                chunks.append(self._create_chunk([{
                                    "type": "Paragraph",
                                    "text": ". ".join(sub_chunk),
                                    "position": item.get("position", {})
                                }]))
                                sub_chunk = []
                                sub_tokens = 0
                        sub_chunk.append(line)
                        sub_tokens += line_tokens
                    if sub_chunk:
                        chunks.append(self._create_chunk([{
                            "type": "Paragraph",
                            "text": ". ".join(sub_chunk),
                            "position": item.get("position", {})
                        }]))
                else:
                    add_chunk()
                    chunks.append(self._create_chunk([item]))
            elif current_tokens + tokens > self.max_tokens:
                add_chunk()
                current_chunk.append(item)
                current_tokens = tokens
            else:
                current_chunk.append(item)
                current_tokens += tokens

        if current_chunk:
            chunks.append(self._create_chunk(current_chunk))

        return chunks

    def _count_tokens(self, text: str) -> int:
        if not text:
            return 0
        if self.model:
            try:
                return len(self.model.encode(text))
            except Exception:
                pass
        return len(text.split())

    def _create_chunk(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Flatten and extract page numbers from nested 'position'
        page_numbers = sorted(set(
            item.get("position", {}).get("page_number")
            for item in items
            if "position" in item and item["position"].get("page_number") is not None
        ))

        # Add page_number to each item as a top-level field
        enriched_items = []
        for item in items:
            item_copy = dict(item)  # Avoid modifying the original
            item_copy["page_number"] = item.get("position", {}).get("page_number")
            enriched_items.append(item_copy)

        return {
            "id": str(uuid.uuid4()),
            "content": enriched_items,
            "tokens": sum(self._count_tokens(self._item_text(item)) for item in enriched_items),
            "page_numbers": page_numbers
        }

    def _item_text(self, item: Dict[str, Any]) -> str:
        if item["type"] == "Table":
            rows = []
            for row in item["content"]:
                row_text = " | ".join(cell.get("text", "") for cell in row)
                rows.append(row_text)
            return "\n".join(rows)
        return item.get("text", "")

def merge_text(content: List[Dict[str, Any]]) -> str:
    merged = []
    for item in content:
        if item["type"] == "Table":
            rows = []
            for row in item["content"]:
                row_text = " | ".join(cell.get("text", "") for cell in row)
                rows.append(row_text)
            merged.append("\n".join(rows))
        else:
            merged.append(item.get("text", ""))
    return "\n\n".join([m for m in merged if m.strip()])
