# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import re, os, sys
from .. import mMaya; reload(mMaya)
from ..mMaya import mSceneInfo; reload(mSceneInfo)
from .. import mLogger; reload(mLogger)
exc = os.path.basename(sys.executable)
logger = mLogger.MLog('moGC.Rules', False if exc == 'mayapy.exe' else True)


def _getSceneInfo():
	"""
	"""
	return mSceneInfo.SceneInfo()


def _get_MS_Env():
	"""
	"""
	proj = os.environ.get('PROJ')
	step = os.environ.get('STEP')
	major = os.environ.get('MAJOR')
	minor = os.environ.get('MINOR')
	
	return {'PROJ': proj, 'STEP': step, 'MAJOR': major, 'MINOR': minor}


def _isMSPipeline():
	"""
	"""
	envSet = _get_MS_Env()
	return {} if envSet.values().count(None) else envSet


def rCurrentSceneName():
	"""
	"""
	sInfo = _getSceneInfo()
	return sInfo.sceneSplitExt


def rWorkingNS():
	"""
	"""
	return ':moGC'


def rViskeyNS():
	"""
	"""
	return ':moGCViskey'


def rNodeOutNS():
	"""
	"""
	return ':moGCOutkey'


def rRigkeyNS():
	"""
	"""
	return ':moGCRigkey'


def rGpuNS():
	"""
	"""
	return ':moGCGPU'


def rRigkeyGrpName():
	"""
	"""
	return 'moGCRigGrp'


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
	return nodeNS.split('_')[0] + re.sub('.*?([0-9]*)$', r'\1', nodeNS)
	#return nodeNS.split('_')[0]


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
	envSet = _isMSPipeline()
	if not envSet:
		sInfo = _getSceneInfo()
		return sInfo.workspaceRoot
	else:
		#shotObj = shotAssetUtils.Project(proj= envSet['PROJ']).stepMajorMinor(envSet['STEP'], envSet['MAJOR'], envSet['MINOR'])
		shotObj = shotAssetUtils.Project(proj= envSet['PROJ'])
		return '/'.join(shotObj.getPath().split(os.sep))


def rGeoCacheRoot():
	"""
	"""
	envSet = _isMSPipeline()
	if not envSet:
		sInfo = _getSceneInfo()
		geoRootPath = ''
		try:
			geoRootPath = sInfo.workspaceRoot + sInfo.dirRule['moGeoCache']
		except:
			logger.error('[moGeoCache] file rule missing.')

		return geoRootPath
	else:
		#shotObj = shotAssetUtils.Project(proj= envSet['PROJ']).stepMajorMinor(envSet['STEP'], envSet['MAJOR'], envSet['MINOR'])
		if envSet['STEP'] == 'fx':
			shotObj = shotAssetUtils.Project(proj= envSet['PROJ']).stepMajorMinor(envSet['STEP'], envSet['MAJOR'], envSet['MINOR'])
			pathSplit = shotObj.getPath('cache').replace('work', 'pub').split(os.sep)
			pathSplit.append('moGeoCache')
			return '/'.join(pathSplit)
		else:
			shotObj = shotAssetUtils.Project(proj= envSet['PROJ'])
			return '/'.join(shotObj.getPath('geoCache').split(os.sep))


def rGeoCacheDir(geoRootPath, assetName, mustMake, sceneName= None):
	"""
	"""
	sInfo = _getSceneInfo()
	isMakeDir = False
	if sceneName is None:
		sceneName = sInfo.sceneSplitExt
	if sceneName is None or mustMake:
		isMakeDir = True

	geoCache_path = sInfo.sep.join([ geoRootPath, assetName, sceneName ])

	if isMakeDir:
		sInfo.makeDir(geoCache_path)

	return geoCache_path


def rXMLFileName(assetName, workingNS, anim_shape):
	"""
	"""
	return '_'.join([ assetName, workingNS.split(':')[1], anim_shape ])


def rXMLFilePath(geoCacheDir, xmlFileName):
	"""
	"""
	sInfo = _getSceneInfo()

	return geoCacheDir + sInfo.sep + xmlFileName + '.xml'


def rGeoListFilePath(geoCacheDir, assetName= None, ves= None, vesShape= None,
	geoFileType= None, makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	if assetName and ves and vesShape and geoFileType:
		fileName = assetName + '_' + vesShape.replace(':', '_') + '@' \
				 + ves.split(':')[-1] + geoFileType
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moGeoList' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)
	
	return filePath


def rViskeyFilePath(geoCacheDir, assetName= None, visAniNode= None,
	makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	if assetName and visAniNode:
		fileName = assetName + '@' \
				 + visAniNode.split(':')[-1].split('|')[-1] \
				 + '_visKeys.ma'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moViskey' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


def rOutkeyFilePath(geoCacheDir, assetName= None, outAniNode= None,
	makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	if assetName and outAniNode:
		fileName = assetName + '@' \
				 + outAniNode.split(':')[-1].split('|')[-1] \
				 + '_outKeys.ma'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moOutkey' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


def rGPUFilePath(geoCacheDir, assetName= None, makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	if assetName:
		fileName = assetName + '_GPU_'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moGPU' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


def rRigkeyFilePath(geoCacheDir, assetName= None, makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	if assetName:
		fileName = assetName + '_rigCtrls.ma'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moRigkey' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


def rTimeInfoFilePath(geoCacheDir, assetName= None, makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	if assetName:
		fileName = assetName + '_timeInfo.txt'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moTimeInfo' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


def rExportLogPath(geoCacheDir, assetName= None, makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	if assetName:
		fileName = assetName + '_exportLog.json'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moExportLog' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


def rGPULogPath(geoCacheDir, assetName= None, makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	if assetName:
		fileName = assetName + '_gpuLog.json'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moGPULog' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


def rGeoMaFilePath(geoCacheDir, assetName= None, makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	shotNum = sInfo.getShotNum(os.path.basename(geoCacheDir))
	if assetName:
		fileName = assetName + '_c' + shotNum + '_GEO_M.ma'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moProxyRef' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


def rGpuMaFilePath(geoCacheDir, assetName= None, makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	shotNum = sInfo.getShotNum(os.path.basename(geoCacheDir))
	if assetName:
		fileName = assetName + '_c' + shotNum + '_GPU_M.ma'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moProxyRef' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


def rLocMaFilePath(geoCacheDir, assetName= None, makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	shotNum = sInfo.getShotNum(os.path.basename(geoCacheDir))
	if assetName:
		fileName = assetName + '_c' + shotNum + '_LOC_M.ma'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moProxyRef' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


def rProxRefFilePath(geoCacheDir, assetName= None, makeDir= None):
	"""
	"""
	sInfo = _getSceneInfo()
	shotNum = sInfo.getShotNum(os.path.basename(geoCacheDir))
	if assetName:
		fileName = assetName + '_c' + shotNum + '_PXRF_M.ma'
	else:
		fileName = ''
	filePath = geoCacheDir + sInfo.sep + 'moProxyRef' + sInfo.sep \
			 + fileName
	if makeDir:
		sInfo.makeDir(filePath, 1)

	return filePath


if _isMSPipeline():
	import shotAssetUtils
	reload(shotAssetUtils)