def extract_text(content) -> str :
    if isinstance(content , str):
        return content
    if isinstance(content , list):
        return "".join(block['text']
                       for block in content
                       if isinstance(block , dict)
                       and block["type"] == 'text'
                       )
    return str(content)