"""print text outputs of an executed notebook (compact). usage: python show_nb.py file.ipynb [max_chars_per_output]"""
import json, sys
nb = json.load(open(sys.argv[1], encoding='utf-8')); lim = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
for i, c in enumerate(nb['cells']):
    if c['cell_type'] != 'code': continue
    for o in c.get('outputs', []):
        if o['output_type'] == 'stream': t = ''.join(o['text'])
        elif o['output_type'] in ('execute_result', 'display_data'):
            t = ''.join(o['data'].get('text/plain', '')) if 'image/png' not in o['data'] else '[image]'
        elif o['output_type'] == 'error': t = 'ERROR ' + o['ename'] + ': ' + o['evalue']
        else: t = ''
        if t.strip(): print(f'--- cell {i} ---\n{t[:lim]}')
