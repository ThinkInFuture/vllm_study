import os
file_name = r'compilation\passes\allgather_chunk_noop_pass.py'
print('basename:', os.path.basename(file_name))
print('dirname:', os.path.basename(os.path.dirname(file_name)))
composite = os.path.basename(os.path.dirname(file_name)) + '\\' + os.path.basename(file_name)
print('composite:', composite)
# My key
print('my key:', 'compilation\\passes\\allgather_chunk_noop_pass.py')