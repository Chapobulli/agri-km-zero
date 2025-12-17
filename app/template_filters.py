# Jinja2 filter to handle both cloudinary URLs and local paths
def url_or_local(path):
    """Returns URL as-is if it starts with http, otherwise prepends /"""
    if not path:
        return ''
    return path if path.startswith('http') else f'/{path}'
