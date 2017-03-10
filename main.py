
"""
Moonshine Geometry Cache Tool
"""

def start():
	import moCache; reload(moCache)
	import moCache.moGeoCacheUI as moGeoCacheUI; reload(moGeoCacheUI)
	moGeoCacheUI.ui_main()