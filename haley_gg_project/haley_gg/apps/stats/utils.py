non_url_safe = [
    '"', '#', '$', '%', '&', '+',
    ',', '/', ':', ';', '=', '?',
    '@', '[', '\\', ']', '^', '`',
    '{', '|', '}', '~', "'", ' ', '-'
]


def slugify(text):
    return text.translate(text.maketrans('', '', u''.join(non_url_safe)))
