def escape_js(s):
    return (s.replace('\\', '\\\\')
             .replace("'", "\\'")
             .replace('\n', '\\n')
             .replace('\r', '\\r'))


test = "Hello\nworld\nbye"
print('input:', repr(test))
print('output:', repr(escape_js(test)))
