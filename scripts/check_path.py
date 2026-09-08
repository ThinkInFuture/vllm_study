import os
file_name = r'attention\context_parallel\attention_cp.py'
basename_only = os.path.basename(file_name)
dirname = os.path.basename(os.path.dirname(file_name))
composite = dirname + '\\' + basename_only
print(f'basename: {basename_only!r}')
print(f'dirname: {dirname!r}')
print(f'composite: {composite!r}')