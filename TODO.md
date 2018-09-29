**TODO**: 
* rework the "equipped" screen to be more of a chart of where equipped items are, rather than a list.
* randomly generated terrain?

Equipment Screen:
* allow for 2d movement on the table
* for 2d movement, use the self.cur_opt[1] (offset) for which col is highlihted

have three lists of equipment going vertically, when the eqp screen is selected change left/right to move between the lists
'floating left': None, 'left arm': None, 'left weapon': None, 'left ring': None, 'left ring': None, 'helmet': None, 'shoulders': None, 'chest': None, 'gloves': None, 'boots': None, 'floating right': None, 'right arm': None, 'right weapon': None, 'right ring': None, 'right ring': None, '

if i < len(current list)

current list coiuld be.... self.cur_text.dialog_opts.len()? 