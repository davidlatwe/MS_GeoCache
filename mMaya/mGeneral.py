# -*- coding:utf-8 -*-
'''
Created on 2016.04.29

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import os, sys
import functools
from .. import mLogger; reload(mLogger)
exc = os.path.basename(sys.executable)
logger = mLogger.MLog('moGC.mMaya.general',
					False if exc == 'mayapy.exe' else True)



def sceneName(shn= None, ext= None):
	"""
	@param: shn 0/1
			ext 0/1, 'ma', 'mb' 
	"""
	shn = True if shn is None or shn else False

	if not untitled():
		# scene is not untitled, do things
		sceneName = cmds.file(q= 1, exn = 1)
		
		# shn
		if shn:
			# return short scene name
			sceneName = os.path.basename(sceneName)
		
		# ext
		if not ext:
			# return without ext
			sceneName = '.'.join(sceneName.split('.')[:-1])
		if ext == 'ma':
			# return mayaAscii file name
			sceneName = '.'.join(sceneName.split('.')[:-1]) + '.ma'
		if ext == 'mb':
			# return mayaBinary file name
			sceneName = '.'.join(sceneName.split('.')[:-1]) + '.mb'

		return sceneName

	else:

		return None


def untitled():
	"""
	"""
	if cmds.file(q= 1, exn = 1).endswith('untitled'):

		return True
	else:

		return False


def namespaceList(current= None):
	"""
	"""
	if not current:
		cmds.namespace(set = ':')

	return cmds.namespaceInfo(lon= 1, r= 1, an= 1)


def namespaceDel(name, wipeOut= None):
	"""
	"""
	for ns in namespaceList():
		if (name in ns) if wipeOut else (name == ns):
			cmds.namespace(f= 1, rm = ns, dnc = 1)


def namespaceSet(name):
	"""
	"""
	if not cmds.namespace(ex = name):
		cmds.namespace(add = name)
	cmds.namespace(set = name)



if __name__ == '__main__':
	pass