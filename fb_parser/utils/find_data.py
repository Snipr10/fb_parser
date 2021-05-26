def find_value(html, key, num_sep_chars=1, separator='"'):
    start_pos = html.find(key)
    if start_pos == -1:
        return None
    start_pos += len(key) + num_sep_chars
    end_pos = html.find(separator, start_pos)
    return html[start_pos:end_pos]
