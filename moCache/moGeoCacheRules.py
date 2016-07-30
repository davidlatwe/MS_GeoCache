# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import re, os, sys
import mMaya.mSceneInfo as mSceneInfo; reload(mSceneInfo)
import mLogger; reload(mLogger)
exc = os.path.basename(sys.executable)
logger = mLogger.MLog('moGC.Rules', False if exc == 'mayapy.exe' else True)


def _getSceneInfo():
	"""
	"""
	return mSceneInfo.SceneInfo()


def rCurrentSceneName():
	"""
	"""
	sInfo = _getSceneInfo()
	return sInfo.sceneSplitExt


def rWorkingNS():
	"""
	"""
	return ':moGeoCache'


def rViskeyNS():
	"""
	"""
	return ':moGeoCacheViskey'


def rNodeOutNS():
	"""
	"""
	return ':moNodeOutkey'


def rRigkeyNS():
	"""
	"""
	return ':moGeoCacheRigkey'


def rGeoFileType():
	"""
	"""
	return '.motxt'


def rAssetNS(node):
	"""
	"""
	return node.split(':')[0]


def rAssetName(nodeNS):
	"""
	Return basename and id string, if nodeNS ends with digi
	"""
	#return nodeNS.split('_')[0] + re.sub('.*?([0-9]*)$', r'\1', nodeNS)
	return nodeNS.split('_')[0]


def rPlaybackRange():
	"""
	"""
	sInfo = _getSceneInfo()

	return (sInfo.palybackStart, sInfo.palybackEnd)


def rFrameRate():
	"""
	"""
	sInfo = _getSceneInfo()

	return sInfo.timeUnit


def rWorkspaceRoot():
	"""
	"""
	sInfo = _getSceneInfo()

	return sInfo.workspaceRoot


def rGeoCacheDir(assetName, mustMake, sceneName= None):
	"""
	"""
	sInfo = _getSceneInfo()
	geoDir = ''
	try:
		geoDir = sInfo.dirRule['moGeoCache']
	except:
		logger.error('[moGeoCache] file rule missing.')

	rootPath = sInfo.workspaceRoot + geoDir
	isMakeDir = False
	if sceneName is None:
		sceneName = sInfo.sceneSplitExt
	if sceneName is None or mustMake:
		isMakeDir = True

	geoCache_path = sInfo.sep.join([ rootPath, assetName, sceneName ])

	if isMakeDir:
		sInfo.makeDir(geoCache_path)

	return geoCache_path


def rXMLFileName(assetName, workingNS, anim_shape):
	"""
	"""
	return '_'.join([ assetName, workingNS.split(':')[1], anim_shape ])


def rGeoListFilePath(geoCacheDir, assetName, ves, vesShape, geoFileType):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '_' + vesShape.replace(':', '_') + '@' + ves.split(':')[-1] + geoFileType
	
	return filePath


def rXMLFilePath(geoCacheDir, xmlFileName):
	"""
	"""
	sInfo = _getSceneInfo()

	return geoCacheDir + sInfo.sep + xmlFileName + '.xml'


def rViskeyFilePath(geoCacheDir, assetName, visAniNode):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '@' + visAniNode.split(':')[-1].split('|')[-1] + '_visKeys.ma'

	return filePath


def rOutkeyFilePath(geoCacheDir, assetName, outAniNode):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '@' + outAniNode.split(':')[-1].split('|')[-1] + '_outKeys.ma'

	return filePath


def rRigkeyFilePath(geoCacheDir, assetName):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '_rigCtrls.ma'

	return filePath


def rTimeInfoFilePath(geoCacheDir, assetName):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '_timeInfo.txt'

	return filePath
