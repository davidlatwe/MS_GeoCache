# -*- coding:utf-8 -*-
'''
Created on 2016.05.18

@author: davidpower
'''
import maya.standalone as standalone
standalone.initialize()

from pymel.core import *
import moCache.moGeoCache as moGeoCache
import moCache.moGeoCacheRules as moRules

import os
import sys
import logging


projPath = 'O:/201603_SongOfKnights/Maya'
filePath = 'O:/201603_SongOfKnights/Maya/scenes/anim/xxx.ma'
assetNode = ''
mode = 'export' if xx else 'import'
paramDict = {}




formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  
logLevel = logging.INFO

logger = logging.getLogger('MayaOil')
ch = logging.StreamHandler()

logger.setLevel(logLevel)
ch.setLevel(logLevel)
ch.setFormatter(formatter)


logger.info('start')


mel.eval('setProject \"' + projPath + '\"')


if mode == 'export':
	file(new= 1, f= 1)
	file(filePath, o= 1, lar= 1, f= 1)
	playbackOptions(min= 1)
	if assetNode:
		select(assetNode, r= 1)
		logger.info('[' + os.path.basename(filePath) + '] Export Start.')
		moGeoCache.exportGeoCache(
			subdivLevel= paramDict['subdiv'],
			isPartial= paramDict['isPartial'],
			isStatic= paramDict['isStatic'],
			assetName_override= paramDict['assetName'],
			sceneName_override= paramDict['sceneName']
			)
	else:
		logger.info('[' + os.path.basename(filePath) + '] Nothing to Export.')
		continue

	logger.info('[' + os.path.basename(filePath) + '] Export Done.')


if mode == 'import' and False:
	file(new= 1, f= 1)
	cacheName = filePath.split('/')[1].split('.')[0]
	geoCacheDir = moRules.rGeoCacheDir(charName, cacheName)
	if not file(geoCacheDir, q= 1, ex= 1):
		logger.info('[' + os.path.basename(filePath) + '] Nothing to Import.')
		continue
	refFile = 'O:/201603_SongOfKnights/Maya/assets/char/' + charFile + '.ma'
	file(refFile, r= 1, type= 'mayaAscii', iv= 1, gl= 1, lrd= 'all', shd= 'renderLayersByName', mnc= 0, ns= charFile, op= 'v=0;')
	select(ls(charName + '*:geo_grp', r= 1), r= 1)
	logger.info('[' + os.path.basename(filePathList[filePath]) + '] Import Start.')
	moGeoCache.importGeoCache(cacheName, assetName= charName)

	mel.eval('source cleanUpScene;')
	mel.eval('putenv "MAYA_TESTING_CLEANUP" "1";')
	mel.eval('scOpt_saveAndClearOptionVars(1);')
	mel.eval('scOpt_setOptionVars( {"unknownNodesOption"} );')
	mel.eval('cleanUpScene( 1 );')
	mel.eval('scOpt_saveAndClearOptionVars(0);')
	mel.eval('putenv "MAYA_TESTING_CLEANUP" "";')

	file(rename= 'O:/201603_SongOfKnights/Maya/scenes/geoCache/' + filePathList[filePath])
	file(s= 1, type='mayaAscii')
	logger.info('[' + os.path.basename(filePathList[filePath]) + '] Import Done.')


logger.info('quit')
quit(force= True)




# C:\Program Files\Autodesk\Maya2016\bin\mayapy.exe" "O:\201603_SongOfKnights\Maya\scripts\moMain.py