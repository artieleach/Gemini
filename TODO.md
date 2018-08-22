**TODO**: 
* create a more robust scripting language. how it stands now, dialog trees will be huuuge
* give each item a designation for where it goes when equipped, eg weapons::hands, rings::fingers, etc
* find out a fast way to put the locations of NPCs into the collision map. may skip that for the most 
part unless the player is nearby? we'll see.
* rework the "equipped" screen to be more of a chart of where equipped items are, rather than a list.
* randomly generated terrain?
* Turn the sprite layer into one just for objects, change dialog items to be actors who dont move, 
for dialog opts, use a defaultdict to easily turn the keys into a list.
* instead of manually making an 800% version of the tilesets, have the image library do that.

currently, the string formatting for dialog options is being done within the dialog object, but it may
be better to do that in the renderer