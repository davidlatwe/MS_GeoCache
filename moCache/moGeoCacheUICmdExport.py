# -*- coding:utf-8 -*-
'''
Created on 2016.05.18

@author: davidpower
'''
from inspect import getsourcefile
import os, sys


def _processEndMsg(fileName, msg):
	"""
	"""
	return ''.join(['\n' * 12,
					'\n'.join(['./' * 16, '\.' * 16]),
					'\n' + '[ ' + fileName + ' ] ' + msg + '\n',
					'\n'.join(['./' * 16, '\.' * 16])
					])

def _checkParam(paramDict):
	"""
	"""
	paramList = [
		'assetName',
		'sceneName',
		'isPartial',
		 'isStatic',
		   'subdiv',
		 'sameName',
		 'conflict'
	]
	logger.debug('PARM:')
	for param in paramList:
		logger.debug(param.rjust(10) + ' : ' + str(paramDict[param]))

def main(projPath, filePath, assetList, paramDict):
	"""
	"""
	# Set Project
	mel.eval('setProject \"' + projPath + '\"')
	# Open File in silent
	scriptEditorInfo(si= 1, sw= 1, se= 1, sr= 1)
	logger.warning('Reading file...')
	openFile(filePath, loadReferenceDepth= 'all', force= True)
	scriptEditorInfo(si= 0, sw= 0, se= 0, sr= 0)
	# 為了待會可能輸出 .ma 檔，先進行 unknow node 的清除
	logger.info('Cleaning unknow nodes...')
	mel.eval('source cleanUpScene;')
	mel.eval('putenv "MAYA_TESTING_CLEANUP" "1";')
	mel.eval('scOpt_saveAndClearOptionVars(1);')
	mel.eval('scOpt_setOptionVars( {"unknownNodesOption"} );')
	mel.eval('cleanUpScene( 1 );')
	mel.eval('scOpt_saveAndClearOptionVars(0);')
	mel.eval('putenv "MAYA_TESTING_CLEANUP" "";')
	# 關閉所有可能的 dynamic
	logger.info('Disable dynamic nodes...')
	[nuc.enable.set(0) for nuc in ls(typ= 'nucleus')]
	[ncl.isDynamic.set(0) for ncl in ls(typ= 'nCloth')]
	[nrg.isDynamic.set(0) for nrg in ls(typ= 'nRigid')]
	[ndc.enable.set(0) for ndc in ls(typ= 'dynamicConstraint')]
	[nhr.simulationMethod.set(0) for nhr in ls(typ= 'hairSystem')]
	[nhr.active.set(0) for nhr in ls(typ= 'hairSystem')]
	# Start
	logger.info('Selecting assets...')
	select(assetList, r= 1)
	logger.debug('Selected assets: \n' + '\n   '.join(cmds.ls(sl= 1)))
	logger.info('Starting GeoCache.')
	# GO
	moGeoCache.exportGeoCache(
		subdivLevel= paramDict['subdiv'],
		isPartial= paramDict['isPartial'],
		isStatic= paramDict['isStatic'],
		assetName_override= paramDict['assetName'],
		sceneName_override= paramDict['sceneName']
		)
	# Done
	logger.info('GeoCache Done.')

if __name__ == '__main__':
	# 取得 package 路徑並置入 sys.path
	# get moudel, add parent-parent directory
	# some say the __file__ attribute is not allways given...
	#parentdir = os.path.dirname(os.path.dirname(__file__))
	#sys.path.insert(0, parentdir)
	current_dir = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
	sys.path.insert(0, current_dir[:current_dir.rfind(os.path.sep)])
	# init
	import maya.standalone as standalone
	standalone.initialize()
	from pymel.core import *
	import maya.cmds as cmds
	import moCache.moGeoCache as moGeoCache
	import mLogger
	logger = mLogger.MLog('moGC.CMD')
	# vars
	projPath = sys.argv[1]
	filePath = sys.argv[2]
	assetList = eval(sys.argv[3])
	paramDict = eval(sys.argv[4])
	# test
	logger.info('PROJ: ' + projPath)
	logger.info('FILE: ' + filePath.split(projPath)[-1])
	logger.info('ASET:\n    ' + '\n    '.join(assetList))
	_checkParam(paramDict)
	# GO
	if assetList and os.path.isfile(filePath):
		main(projPath, filePath, assetList, paramDict)
		fileName = str(system.sceneName().basename())
		newFile(force= True)
		cmds.quit(force= True)
		logger.info(_processEndMsg(fileName, 'Export Done.'))
	elif os.path.isfile(filePath):
		fileName = os.path.basename(filePath)
		logger.error(_processEndMsg(fileName, 'Nothing to Export.'))
	else:
		logger.debug(filePath)
		logger.critical(_processEndMsg('None', 'File not exists.'))
	
	raw_input()
