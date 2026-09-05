def extract_text(content) -> str:
    try:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        return str(content)
    except Exception:
        return str(content) if content is not None else ""