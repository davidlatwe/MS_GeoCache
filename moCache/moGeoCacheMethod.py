# -*- coding:utf-8 -*-
'''
Created on 2016.05.12

@author: davidpower
'''
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
from .. import mMaya; reload(mMaya)
from ..mMaya import mOutliner; reload(mOutliner)
from ..mMaya import mGeneral; reload(mGeneral)
import os, sys
import json
from .. import mLogger; reload(mLogger)
exc = os.path.basename(sys.executable)
logger = mLogger.MLog('moGC.Method', False if exc == 'mayapy.exe' else True)


def _xList(l):
	"""
	"""
	if l is None:
		return []
	return l


def mCleanWorkingNS(workingNS):
	"""
	"""
	mGeneral.namespaceDel(workingNS)


def mSetupWorkingNS(workingNS):
	"""
	"""
	mGeneral.namespaceSet(workingNS)


def mSetStaticRange(timelineInfo= None):
	"""
	"""
	if timelineInfo:
		cmds.playbackOptions(min= timelineInfo[0], max= timelineInfo[1])
	else:
		timelineInfo = [cmds.playbackOptions(q= 1, min= 1),
						cmds.playbackOptions(q= 1, max= 1)]
		cmds.playbackOptions(max= cmds.playbackOptions(q= 1, min= 1) + 1)
		
		return timelineInfo


def mRangePushBack(restore= None):
	"""
	"""
	if restore:
		cmds.playbackOptions(max= cmds.playbackOptions(q= 1, max= 1) - 1)
	else:
		cmds.playbackOptions(max= cmds.playbackOptions(q= 1, max= 1) + 1)


def mProcQueue():
	"""
	找出所選取的物件的根物件，並做名稱排序後回傳
	"""
	expList = []

	''' list out objs '''
	# << get selection's root transform node >>
	expList = mOutliner.findRoot('transform')
	expList.sort()

	return expList


def mPartialQueue(partialDict):
	"""
	"""
	selection = cmds.ls(sl= 1, l= 1)
	for rootNode in partialDict.keys():
		for dag in selection:
			if dag.startswith('|' + rootNode):
				partialDict[rootNode].append(dag.split('|')[-1].split(':')[-1])
				dagShape = cmds.listRelatives(dag, s= 1, ni= 1)
				if dagShape:
					partialDict[rootNode].append(dagShape[0].split(':')[-1])

	return partialDict


def mFilterOut(rootNode, outNodeDict):
	"""
	重要的核心函式，判斷各種狀況來過濾不必要的物件
	"""
	# meshes need to process
	''' 內容為 Mesh '''
	anim_meshes = []
	# meshes have visible animation
	''' 內容為 Mesh 或 Transform '''
	anim_viskey = []

	def _set(mylist):
		# 先檢查 list 是否為 None，再轉 set (去掉重複物件)
		return set(mylist) if mylist else set([])

	''' anim_meshes 濾掉 [intermediate Shape] '''
	# FILTER OUT # <intermediate objects>
	_allMesh = cmds.listRelatives(rootNode, ad= 1, f= 1, typ= 'mesh')
	itrm_meshes = _set(mOutliner.findIMObj(rootNode))
	anim_meshes = _set(_allMesh) - itrm_meshes

	''' anim_meshes 濾掉 [完全隱藏] 物件 並擷取有 key 的物件到 anim_viskey '''
	 # FILTER OUT # <constant hidden objects>
	for obj in cmds.listRelatives(rootNode, ad= 1, f= 1):
		objShouldRemove = False
		if cmds.attributeQuery('visibility', ex= 1, node = obj):
			# 檢查 visibility 是否有連接其他 input
			# 目前的判定方式為，只要有連接
			# 就假定該 input 為 animCurve, expression 或 drivenKey
			if not cmds.listConnections(obj + '.v'):
				if not cmds.getAttr(obj + '.v'):
					# 此物件為 [完全隱藏] 的 [Dag]
					objShouldRemove = True
					logger.debug('No visibility key -x [' + obj.split('|')[-1]
								+ ']')
			else:
				# do something if has key,
				# expression or drivenKey connected to visibility
				drivers = cmds.setDrivenKeyframe(obj + '.v', q= 1, dr= 1)
				if drivers[0] == 'No drivers.':
					# has key or expression
					objHasViskey = False
					objShp = cmds.listRelatives(obj, s= 1, f= 1)
					if cmds.objectType(obj) == 'transform' and objShp:
						if cmds.objectType(objShp[0]) == 'mesh':
							# 此物件為 [沒有 DrivenKey] 的 [Mesh]
							# 但 [有 key 在 Transform]
							objHasViskey = True
					if cmds.objectType(obj) == 'mesh':
						# 此物件為 [沒有 DrivenKey] 的 [Mesh]
						# 但 [有 key 在 Shape]
						objHasViskey = True

					''' 登記至 < anim_viskey > '''
					if objHasViskey:
						# 此物件為 [有 key] 的 [Mesh]
						anim_viskey.append(obj)
						logger.debug('Visibility key detected -> [' \
									+ obj.split('|')[-1] + ']')
					else:
						# 此物件為 [有 key] 的 [非Mesh]
						pass
				else:
					# is a driven obj
					driverHasViskey = False
					driverHasOutkey = False
					# 檢查所有 Driver
					for driver in drivers:
						# 檢查這個 Driver 是否有登錄在 outNodeDict 清單裡
						# driver 可能為 [curve 控制器]
						# 		   或是 [受 curve 控制器 控制的 util 節點]
						driver_ln = driver.split('.')[0]
						driver_at = driver.split('.')[1]
						driver_sn = driver_ln.split(':')[-1]
						goingOut = False
						if outNodeDict:
							if driver_sn in outNodeDict.keys():
								# Driver [已登錄於 outNodeDict]
								goingOut = True
							else:
								driver_ctrl = _xList(cmds.listConnections(
												driver_ln, d= 0, p= 1))
								for dc in driver_ctrl:
									driver_ctrl_sn = \
										dc.split(':')[-1].split('.')[0]
									if driver_ctrl_sn in outNodeDict.keys():
										# Driver [未登錄於 outNodeDict]
										# 但
										# 控制此 Drive 的控制器
										#		 [已登錄於 outNodeDict]
										logger.debug('Visibility driverCTRL' \
											+ 'in [outNodeDict] ->' \
											+ '[' + dc + '] - ' \
											+ '[' + driver_ln + ']')
										driver_sn = driver_ctrl_sn
										driver_at = dc.split('.')[1]
										goingOut = True
										break
						if goingOut and driver_at in outNodeDict[driver_sn]:
							# 這個 Driver 已登錄，
							# 為避免之後 import Visibility 衝突就略過
							objShp = cmds.listRelatives(obj, s= 1, f= 1)
							if cmds.objectType(obj) == 'transform' and objShp:
								if cmds.objectType(objShp[0]) == 'mesh':
									# 此物件為 [有 DrivenKey] 的 [Mesh]
									# 且 [在 Transform]
									# 但 [已登錄於 outNodeDict]
									logger.debug('Visibility driver in ' \
										+ '[outNodeDict] -> [' + driver + ']' \
										+ ' - [' + obj.split('|')[-1] + ']')
									driverHasOutkey = True
									break
							if cmds.objectType(obj) == 'mesh':
								# 此物件為 [有 DrivenKey] 的 [Mesh]
								# 且 [在 Shape]
								# 但 [已登錄於 outNodeDict]
								logger.debug('Visibility driver in ' \
									+ '[outNodeDict] -> [' + driver + ']' \
									+ ' - [' + obj.split('|')[-1] + ']')
								driverHasOutkey = True
								break
						# 檢查這個 Driver 是否有 Key
						if cmds.listConnections(driver, s= 1, d= 0):
							objShp = cmds.listRelatives(obj, s= 1, f= 1)
							if cmds.objectType(obj) == 'transform' and objShp:
								if cmds.objectType(objShp[0]) == 'mesh':
									# 此物件為 [有 DrivenKey] 的 [Mesh]
									# 且 [在 Transform]
									driverHasViskey = True
									break
							if cmds.objectType(obj) == 'mesh':
								# 此物件為 [有 DrivenKey] 的 [Mesh]
								# 且 [在 Shape]
								driverHasViskey = True
								break

					''' 登記至 < anim_viskey > '''
					if driverHasViskey:
						# 此物件為 [有 DrivenKey] 且 [有設 key] 的 [Mesh]
						anim_viskey.append(obj)
						logger.debug('Visibility drivenKey detected -> [' \
									+ obj.split('|')[-1] + ']')
					else:
						if not cmds.getAttr(obj + '.v'):
							objShouldRemove = not driverHasOutkey
							if objShouldRemove:
								# 此物件為 [有 DrivenKey]
								# 但 [沒有設 key]
								# 且 [隱藏] 的 [Mesh]
								logger.debug('No visibility drivenKey -x [' \
											+ obj.split('|')[-1] + ']')
							else:
								# 此物件為 [有 DrivenKey]
								# 但 [已登錄於 outNodeDict] 的 [Mesh]
								pass
						else:
							# 此物件為 [有 DrivenKey]
							# 雖然 [沒有設 key]
							# 但為 [顯示] 的 [Mesh]
							pass
			
			''' 調整 < anim_meshes > '''
			if objShouldRemove:
				if cmds.objectType(obj) == 'transform':
					# 假若此物件 Transform 為隱藏且底下還有子物件，
					# 就連同所有子物件從 Cache 清單移除
					hiddenChild = _set(cmds.listRelatives(obj, ad= 1, f= 1))
					if hiddenChild:
						anim_meshes = anim_meshes - hiddenChild
				if cmds.objectType(obj) == 'mesh':
					# 移除這個 Mesh
					if obj in anim_meshes:
						anim_meshes.remove(obj)

	return anim_meshes, anim_viskey


def mDuplicateSelectedOnly(grpName, doConstrain= None):
	"""
	"""
	targetList = pm.ls(sl= 1)
	desGrp = pm.group(n= grpName, w= 1, em= 1)
	newDags = []
	for target in targetList:
		par = pm.duplicate(target, po=1)[0]
		pm.parent(par, desGrp)
		par.rename(target)
		shp = pm.duplicate(target.getShape(), addShape=True)[0]
		shp.setParent(par, s= 1)
		new = par.getChildren()[0]
		pm.parent(new, desGrp)
		n = par.name()
		pm.delete(par)
		new.rename(n)
		# currently return string type for cmds cmd
		newDags.append(new.name())
		if doConstrain:
			pm.parentConstraint(target, new, mo= 1)

	return newDags


def mBakeViskey(anim_viskey, playbackRange):
	"""
	"""
	cmds.bakeResults(anim_viskey, at= '.v', t= playbackRange, sm= 1, s= 0)


def mBakeOutkey(outNodeDict, playbackRange, assetNS):
	"""
	"""
	def findObj(dag):
		targetList = cmds.ls('*' + dag, r= 1, l= 1, et= 'transform')
		inverseResult = []
		for T in targetList:
			if not T.startswith('|' + assetNS):
				inverseResult.append(T)
		return list(set(targetList) - set(inverseResult))

	for obj in outNodeDict:
		attrs = outNodeDict[obj]
		result = findObj(obj)
		if len(result) == 1:
			cmds.bakeResults(result[0], at= attrs, t= playbackRange,
				sm= 1, s= 0)


def mBakeRigkey(rigCtrlList, playbackRange):
	"""
	"""
	cmds.bakeResults(rigCtrlList, at= ['.t', '.r', '.s'], t= playbackRange,
					sm= 1, s= 0)
	for ctrl in rigCtrlList:
		findPC = cmds.listRelatives(ctrl, c= 1, typ= 'parentConstraint')
		for pc in _xList(findPC):
			cmds.delete(pc)


def mDuplicateViskey(anim_viskey):
	"""
	"""
	visAniNodeList = []
	for visNode in anim_viskey:
		aniNode = cmds.listConnections(visNode + '.visibility')[0]
		visAniNodeList.append(cmds.duplicate( aniNode,
			n= visNode.split('|')[-1] )[0])

	return visAniNodeList


def mDuplicateOutkey(outNodeDict, assetNS):
	"""
	"""
	def findObj(dag):
		targetList = cmds.ls('*' + dag, r= 1, l= 1, et= 'transform')
		inverseResult = []
		for T in targetList:
			if not T.startswith('|' + assetNS):
				inverseResult.append(T)
		return list(set(targetList) - set(inverseResult))

	outAniNodeDict = {}
	for obj in outNodeDict:
		result = findObj(obj)
		if len(result) == 1:
			r = result[0]
			for attr in outNodeDict[obj]:
				rAttr = r + '.' + attr
				# 找出剛剛 bake 出來的 animationCurve
				aniNode = cmds.listConnections(rAttr, d= 0)[0]
				# 複製進作業的 namespace
				aniNode = cmds.duplicate(aniNode, n= r.split('|')[-1])[0]
				# 紀錄該控制器參數輸出的目的地
				outAniNodeDict[aniNode] = cmds.listConnections(rAttr,
					scn= 1, s= 0, p= 1)

	return outAniNodeDict


def mPolyUniteMesh(anim_meshes):
	"""
	"""
	# create a group for geoCaching carrier
	ves_grp = cmds.group(em= 1, n= 'polyUniteVesGrp')
	# convert meshes by polyUnite node into geoCaching carrier
	for animShp in anim_meshes:
		# get transform node's name without namespace
		animTrans = cmds.listRelatives(animShp, p= 1)[0].split(':')[-1]
		# create a polyCube as a carrier for geoCaching and match name 
		vesTrans = cmds.polyCube(n= animTrans, ch= 0)[0]
		# rename polyCube's shape node to match name
		vesShape = cmds.rename(cmds.listRelatives(vesTrans, s= 1)[0], animShp)
		# put in to the geoCaching carrier's group
		cmds.parent(vesTrans, ves_grp)
		# create polyUnite node
		pUnite = cmds.createNode('polyUnite', n= 'polyUnite_' + animTrans)
		# carrier load up
		cmds.connectAttr(animShp + '.worldMatrix', pUnite + '.inputMat[0]')
		cmds.connectAttr(animShp + '.worldMesh', pUnite + '.inputPoly[0]')
		cmds.connectAttr(pUnite + '.output', vesShape + '.inMesh')

	return ves_grp


def mSmoothMesh(ves, subdivLevel):
	"""
	"""
	logger.info('Smoothing : ' + ves)
	cmds.polySmooth(ves, mth= 0, sdt= 2, ovb= 1, ofb= 3, ofc= 0, ost= 1,
							ocr= 0, dv= subdivLevel, bnr= 1 ,c= 1, kb= 1,
							ksb= 1, khe= 0, kt= 1, kmb= 1, suv= 1, peh= 0,
							sl= 1, dpe= 1, ps= 0.1, ro= 1, ch= 0)


def mSaveGeoList(geoListFile):
	"""
	write out an empty file, we only need file name
	"""
	with open(geoListFile, 'w') as geomoTxt:
		pass


def mLoadGeoList(exportLogDict, geoListDir, workingNS, geoFileType):
	"""
	"""
	anim_geoDict = {}

	workingNS = workingNS.split(':')[-1]
	logger.debug('geoListDir:\n' + geoListDir)
	if os.path.exists(geoListDir):
		for geoFile in os.listdir(geoListDir):
			if geoFile.endswith(geoFileType):
				if geoFile in exportLogDict['geo']:
					geo = geoFile.split(workingNS + '_')[-1]
					geo = geo.split(geoFileType)[0]
					geo_trans = geo.split('@')[1]
					geo_shape = geo.split('@')[0]
					anim_geoDict[geo_trans] = geo_shape
				else:
					logger.debug('GEO: Import skipped [' + geoFile + ']')

	return anim_geoDict


def mLoadVisKeyList(exportLogDict, visKeyDir, mayaFileType):
	"""
	"""
	visAniNodeList = []
	logger.debug('visKeyDir:\n' + visKeyDir)
	if os.path.exists(visKeyDir):
		for mayaFile in os.listdir(visKeyDir):
			if mayaFile.endswith(mayaFileType):
				if mayaFile in exportLogDict['visKey']:
					visAniNode = mayaFile.split('@')[1].split(mayaFileType)[0]
					visAniNodeList.append(visAniNode)

	return visAniNodeList


def mLoadOutKeyList(exportLogDict, outKeyDir, jsonFileType):
	"""
	"""
	outAniNodeList = []
	logger.debug('outKeyDir:\n' + outKeyDir)
	if os.path.exists(outKeyDir):
		for jsonFile in os.listdir(outKeyDir):
			if jsonFile.endswith(jsonFileType):
				if jsonFile in exportLogDict['outKey']:
					outAniNode = jsonFile.split('@')[1].split(jsonFileType)[0]
					outAniNodeList.append(outAniNode)

	return outAniNodeList


def mLoadGpuList(exportLogDict, gpuListDir, gpuFileType):
	"""
	"""
	gpuList = []
	gpuListDir = os.path.dirname(gpuListDir)
	logger.debug('gpuListDir:\n' + gpuListDir)
	if os.path.exists(gpuListDir):
		for gpuFile in os.listdir(gpuListDir):
			if gpuFile.endswith(gpuFileType):
				if gpuFile in exportLogDict['gpu']:
					gpuList.append(gpuFile)

	return gpuList


def mExportViskey(keyFile):
	"""
	輸出 visible key
	"""
	cmds.file(keyFile, f= 1, op= "v=0;", typ= "mayaAscii", es= 1)


def mImportViskey(keyFile, assetNS, assetName, visAniNode):
	"""
	"""
	visAniMesh = ''
	targetList = cmds.ls('*' + visAniNode.split(':')[-1], r= 1, l= 1)
	
	try:
		stw = lambda s : s.startswith('|' + assetNS)
		visAniMesh = [target for target in targetList if stw(target)][0]
	except:
		logger.warning('viskey target not found ' \
			+ '[' + visAniNode.split(':')[-1] + '] -x')
		return

	isIMO = cmds.getAttr(visAniMesh + '.intermediateObject')
	if cmds.objectType(visAniMesh) == 'mesh' and isIMO:
		visAniTran = cmds.listRelatives(visAniMesh, p= 1)[0]
		visAniMesh = cmds.listRelatives(visAniTran, s= 1, ni= 1, f= 1)[0]
	
	try:
		inputAni = cmds.listConnections(visAniMesh + '.visibility', p= 1,
			t= 'animCurve')
		if inputAni:
			try:
				cmds.disconnectAttr(inputAni[0], visAniMesh + '.visibility')
				cmds.delete(inputAni[0].split('.')[0])
				logger.warning('viskey PARTIAL deleted. [' + inputAni[0] + ']')
			except:
				logger.warning('viskey PARTIAL delete failed. ' \
					+ '[' + inputAni[0] + ']')
		cmds.file(keyFile, i= 1, typ= 'mayaAscii', iv= 1, mnc= 1,
			ns= ':' + assetName)
		cmds.connectAttr(visAniNode + '.output', visAniMesh + '.visibility')
		logger.info('viskey target connected. ' \
			+ '[' + visAniNode.split(':')[-1] + '] -> {' + visAniMesh + '}')
	except:
		logger.warning('viskey target connection failed. ' \
			+ '[' + visAniNode.split(':')[-1] + '] -x {' + visAniMesh + '}')


def mExportOutkey(keyFile, outAniNode, inputList):
	"""
	輸出 outNode key
	"""
	jsonFile = keyFile.replace('_outKeys.ma', '_input.json')
	jsonData = {outAniNode : inputList}
	with open(jsonFile, 'w') as json_file:
		json.dump(jsonData, json_file, indent=4)

	cmds.file(keyFile, f= 1, op= "v=0;", typ= "mayaAscii", es= 1)

	return jsonFile


def mImportOutkey(keyFile, assetNS, assetName, outAniNode):
	"""
	"""
	inputDict = {}
	jsonFile = keyFile.replace('_outKeys.ma', '_input.json')
	with open(jsonFile, 'r') as json_file:
		inputDict = json.load(json_file)

	imported = False
	outNode = inputDict.keys()[0]
	for inTarget in inputDict[outNode]:
		targetList = cmds.ls('*' + inTarget.split(':')[-1], r= 1, l= 1)
		
		try:
			stw= lambda s: s.startswith('|' + assetNS) or s.startswith(assetNS)
			inNode = [target for target in targetList if stw(target)][0]
		except:
			logger.warning('[' + outAniNode + '] input target not found ' \
				+ '[' + inTarget.split(':')[-1] + '] -x')
			continue
		
		try:
			inputAni = cmds.listConnections(inNode, p= 1, d= 0, scn= 1)
			if inputAni:
				try:
					cmds.disconnectAttr(inputAni[0], inNode)
					cmds.delete(inputAni[0].split('.')[0])
					logger.warning('outkey PARTIAL deleted. ' \
						+ '[' + inputAni[0] + ']')
				except:
					logger.warning('outkey PARTIAL delete failed. [' \
						+ inputAni[0] + ']')
			if not imported:
				cmds.file(keyFile, i= 1, typ= 'mayaAscii', iv= 1, mnc= 1,
					ns= ':' + assetName)
				imported = True
			cmds.connectAttr(outAniNode + '.output', inNode)
			logger.info('outNode target connected. [' + outAniNode + ']' \
				+ ' -> {' + inNode + '}')
		except:
			logger.warning('outNode target connection failed. ' \
				+ '[' + outAniNode + '] -x {' + inNode + '}')


def mExportRigkey(rigFile):
	"""
	輸出 rigging ctrls
	"""
	cmds.file(rigFile, f= 1, op= "v=0;", typ= "mayaAscii", es= 1)


def mImportRigkey(rigFile, assetName):
	"""
	"""
	cmds.file(rigFile, i= 1, typ= 'mayaAscii', iv= 1, mnc= 1,
		ns= ':' + assetName)


def mExportGeoCache(geoCacheDir, assetName):
	"""
	設定 geoCache 參數並執行
	"""
	# doCreateGeometryCache( int $version, string $args[] )
	# C:/Program Files/Autodesk/Maya2016/scripts/others/
	# 	doCreateGeometryCache.mel
	version = 6

	def _gcArgs():
		# time range mode:
		# 		mode = 0 : use $args[1] and $args[2] as start-end
		# 		mode = 1 : use render globals
		# 		mode = 2 : use timeline
		timerangeMode = 2
		# start frame (if time range mode == 0)
		startFrame = 0
		# end frame (if time range mode == 0)
		endFrame = 0
		# cache file distribution, either "OneFile" or "OneFilePerFrame"
		cacheDistr = 'OneFilePerFrame'
		# 0/1, whether to refresh during caching
		refresh = '0'
		# directory for cache files, if "", then use project data dir
		cacheDir = geoCacheDir
		# 0/1, whether to create a cache per geometry
		perGeo = 1
		# name of cache file. An empty string can be used to
		# specify that an auto-generated name is acceptable.
		cacheName = assetName
		# 0/1, whether the specified cache name is to be used as a prefix
		usePrefix = 1
		# action to perform: "add", "replace", "merge",
		#					 "mergeDelete" or "export"
		action = 'export'
		# force save even if it overwrites existing files
		force = 1
		# simulation rate, the rate at which the cloth simulation
		# is forced to run
		simRate = 1
		# sample mulitplier, the rate at which samples are written,
		# as a multiple of simulation rate.
		sample = 1
		# 0/1, whether modifications should be inherited
		# from the cache about to be replaced.
		# Valid only when action = "replace".
		inherited = 0
		# 0/1, whether to store doubles as floats
		storeFloat = 1
		# name of cache format: "mcc", "mcx"
		cFormat = 'mcx'
		# 0/1, whether to export in local or world space
		space = 0

		return locals()

	def _qts(var):
		# surround string with double quote
		return '"' + str(var) + '"'

	# get all geoCache inputs value 
	args = [ _qts(_gcArgs()[var]) for var in _gcArgs.__code__.co_varnames ]
	# make cmd and do GeoCache
	evalCmd = 'doCreateGeometryCache ' + str(version) + \
			  ' {' + ', '.join(args) + '};'
	logger.debug('GeoCache export CMD : ' + evalCmd)
	mel.eval(evalCmd)


def mImportGeoCache(xmlFile, assetNS, animTran, conflictList,
	ignorDuplicateName, staticInfo):
	"""
	import 時，如果該物件的 shape vis 為隱藏，會跳過
	"""
	def importGeoProcess(dag):
		inputAni = []
		anim_relatives = cmds.listRelatives(dag, s= 1, ni= 1, f= 1)
		if anim_relatives:
			animShp = anim_relatives[0]
			if cmds.objectType(animShp) != 'mesh':
				return
			if not cmds.getAttr(animShp + '.v'):
				# check if shape node is hidden by visKey
				inputAni = cmds.listConnections(animShp + '.visibility',
					p= 1, t= 'animCurve')
				if inputAni:
					cmds.disconnectAttr(inputAni[0], animShp + '.visibility')
					cmds.setAttr(animShp + '.v', 1)
				else:
					return
			cmds.select(dag, r= 1)
			# delete cache
			for obj in cmds.ls(sl= 1):
				cacheDeleted = 0
				hist = cmds.listHistory(obj, pdo= 1)
				if hist:
					for histNode in hist:
						if cmds.nodeType(histNode) == 'cacheFile':
							cmds.delete(histNode)
							cacheDeleted = 1
				if not cacheDeleted:
					logger.info('No caches Del. -> ' + obj)
			# import new cache
			mel.eval('source doImportCacheArgList')
			mel.eval('importCacheFile "' + xmlFile + '" "Best Guess"')
			if inputAni:
				cmds.connectAttr(inputAni[0], animShp + '.visibility')
			if staticInfo and staticInfo[0]:
				for histNode in cmds.listHistory(dag, pdo= 1):
					if cmds.nodeType(histNode) == 'cacheFile':
						cmds.setAttr(histNode + '.hold', staticInfo[1] + 1)
		else:
			logger.warning('This node might not contenting shape node, ' \
						+ 'but source rigging file dose.')

	targetList = cmds.ls('*' + animTran, r= 1, l= 1, et= 'transform')
	# conflictList: if conflict string included in dag name,
	# remove in next step
	inverseResult = []
	for T in targetList:
		if not T.startswith('|' + assetNS):
			inverseResult.append(T)
		for C in conflictList:
			if C in T:
				inverseResult.append(T)
	animTranList = list(set(targetList) - set(inverseResult))
	if len(animTranList) == 1:
		importGeoProcess(animTranList[0])
	elif len(animTranList) > 1:
		logger.warning('Conflict, too many target -> ' + animTran)
		for trans in animTranList:
			logger.warning('-x ' + trans)
			if ignorDuplicateName:
				logger.warning('Ignor duplicate names... ')
				importGeoProcess(trans)
	else:
		logger.warning('No target found -> ' + animTran)


def mExportGPUCache(ves_grp, playbackRange, gpuName):
	"""
	輸出 GPU cache, 目前為多檔案輸出
	多檔案輸出時, saveMultipleFiles= True, 以及使用 filePrefix
	單檔案輸出時, saveMultipleFiles= False, 使用 fileName
	"""
	ves_member = cmds.listRelatives(ves_grp, c= 1)
	st = playbackRange[0]
	et = playbackRange[1]
	dirPath = os.path.dirname(gpuName)
	single = ''
	prefix = os.path.basename(gpuName)
	result = cmds.gpuCache(ves_member, startTime= st, endTime= et,
						optimize= 1, optimizationThreshold= 40000,
						writeMaterials= 1, dataFormat= 'ogawa',
						saveMultipleFiles= True,
						directory= dirPath,
						filePrefix= prefix, fileName= single)
	return result


def mImportGPUCache(gpuListDir, gpuFile, gpuGrp, assetName, gpuNS):
	"""
	"""
	gpuNS = ':' + assetName + gpuNS + ':'
	gpuBase = gpuFile.split('.')[0]
	gpuNode = gpuNS + 'gpu' + gpuBase.split('_GPU_')[1]
	gpuPath = gpuListDir.replace(os.path.basename(gpuListDir), gpuFile)
	gpuShape = pm.createNode('gpuCache', n= gpuNode + 'Shape')
	gpuTrans = gpuShape.getParent().rename(gpuNode).setParent(gpuGrp)
	gpuShape.cacheFileName.set(gpuPath)


def mExportTimeInfo(timeInfoFile, timeUnit, playbackRange, isStatic):
	"""
	"""
	timeInfo = timeUnit + '\n' + str(playbackRange[0]) + ':' \
		+ str(playbackRange[1]) \
		+ '\nisStatic = ' + str(isStatic)
	with open(timeInfoFile, 'w') as timeInfoTxt:
		timeInfoTxt.write(timeInfo)


def mImportTimeInfo(timeInfoFile):
	"""
	"""
	with open(timeInfoFile, 'r') as timeInfoTxt:
		timeInfo = timeInfoTxt.read().split('\n')
		cmds.currentUnit(t= timeInfo[0])
		logger.info('TimeInfo   [Unit] ' + timeInfo[0])
		cmds.playbackOptions(min= float(timeInfo[1].split(':')[0]))
		cmds.playbackOptions(max= float(timeInfo[1].split(':')[1]))
		logger.info('TimeInfo  [Range] ' + timeInfo[1])
		exec(timeInfo[2])
		logger.info('TimeInfo [Static] ' + str(isStatic))
		
		return [isStatic, float(timeInfo[1].split(':')[1])]


def mExportLogDump(logPath, exportLogDict, isPartial= None):
	"""
	"""
	if isPartial:
		pLog = exportLogDict
		exportLogDict = mExportLogRead(logPath)
		for k in exportLogDict:
			exportLogDict[k].extend(pLog[k])
			exportLogDict[k] = list(set(exportLogDict[k]))

	if exportLogDict:
		with open(logPath, 'w') as json_file:
			json.dump(exportLogDict, json_file, indent=4)


def mExportLogRead(logPath):
	"""
	"""
	if not os.path.isfile(logPath):
		logger.warning('ExportLog not found.')

		return None
	try:
		with open(logPath) as json_file:

			return json.load(json_file)
	except:
		logger.error('Error while reading exportLog.')

		return {}


def mFindWrapObjsName(wSource, wTarget, assetNS, conflictList):
	"""
	"""
	def findObj(dag):
		targetList = cmds.ls('*' + dag, r= 1, l= 1, et= 'transform')
		# conflictList: if conflict string included in dag name,
		# remove in next step
		inverseResult = []
		for T in targetList:
			if not T.startswith('|' + assetNS):
				inverseResult.append(T)
			for C in conflictList:
				if C in T:
					inverseResult.append(T)
		return list(set(targetList) - set(inverseResult))

	newSource = ''
	result = findObj(wSource)
	if len(result) == 1:
		newSource = result[0]

	newTarget= []
	for wt in wTarget:
		result = findObj(wt)
		if len(result) == 1:
			newTarget.append(result[0])

	return newSource, newTarget


def mWrapSourceHasCached(wSource):
	"""
	"""
	hist = cmds.listHistory(wSource, pdo= 1)
	for histNode in _xList(hist):
		if cmds.nodeType(histNode) == 'cacheFile':
			return True
	return False


def mDoWrap(wSource, wTarget):
	"""
	設定 geoCache 參數並執行
	"""
	# doWrapArgList( string $version, string $args[] )
	# C:/Program Files/Autodesk/Maya2016/scripts/others/
	# 	doWrapArgList.mel
	version = 7

	def _gcArgs():
		# operation:
		# 		1 - Create a new wrap
		# 		2 - Add influence
		# 		3 - Remove influence
		operation = 1
		# threshold:  The weight threshold to be used when creating a wrap
		threshold = 0
		# maxDist  :  The maxDistance to be used when creating a wrap
		maxDist = 1
		# inflType :  The influence type (1 = point, 2 = face)
		inflType = 2
		# exclusiveBind :  Bind algorithm (0=smooth, 1=exclusive)
		exclusiveBind = 0
		# autoWeightThreshold :  Auto weight threshold control
		autoWeightThreshold = 1
		# renderInfl :  Render influence objects
		renderInfl = 0
		# falloffMode :  Distance falloff algorithm
		falloffMode = 0

		return locals()

	def _qts(var):
		# surround string with double quote
		return '"' + str(var) + '"'

	# get all geoCache inputs value 
	args = [ _qts(_gcArgs()[var]) for var in _gcArgs.__code__.co_varnames ]
	# make cmd and do GeoCache
	evalCmd = 'doWrapArgList "' + str(version) + \
			  '" {' + ', '.join(args) + '};'
	logger.debug('Wrap CMD : ' + evalCmd)

	cmds.select(wTarget, r= 1)
	cmds.select(wSource, add= 1)
	mel.eval(evalCmd)


def mRemoveWrap(wSourceBat, wTargetBat):
	"""
	"""
	for wt in wTargetBat:
		hist = cmds.listHistory(wt, pdo= 1)
		for histNode in _xList(hist):
			if cmds.nodeType(histNode) == 'wrap':
				sName = list(set(cmds.listConnections(histNode,
					t= 'transform')))[0]
				if sName in [ws.split('|')[-1] for ws in wSourceBat]:
					cmds.delete(histNode)
					break


def mGetSmoothMask(assetName):
	"""
	"""
	smoothmask = []
	smoothExclusive = False
	setList = cmds.ls('*moGCSmoothMask', r= 1, typ= 'objectSet')
	for set in _xList(setList):
		if ':' not in set or (':' in set and set.startswith(assetName)):
			for obj in cmds.sets(set, q= 1, no= 1):
				smoothmask.append(obj.split(':')[-1])
			if cmds.attributeQuery('smoothExclusive', node= set, ex= 1):
				if cmds.getAttr(set + '.smoothExclusive'):
					smoothExclusive = True 
				else:
					smoothExclusive = False
				break
				
	return smoothExclusive, smoothmask


def mGetRigCtrlExportList(assetName):
	"""
	"""
	rigCtrlList = []
	setList = cmds.ls('*moGCRigCtrlExport', r= 1, typ= 'objectSet')
	for set in _xList(setList):
		if ':' not in set or (':' in set and set.startswith(assetName)):
			for obj in cmds.sets(set, q= 1, no= 1):
				rigCtrlList.append(obj)
			break
				
	return rigCtrlList


def mGetWrappingList(assetName):
	"""
	"""
	wrapDict = {}
	setList = cmds.ls('*moGCWrap_*', r= 1, typ= 'objectSet')
	for set in _xList(setList):
		if ':' not in set or (':' in set and set.startswith(assetName)):
			srcObj = cmds.getAttr(set + '.wrapSource')
			members = cmds.sets(set, q= 1, no= 1)
			# remove srcObj
			for m in members:
				if m.endswith(srcObj):
					members.remove(m)
					break
			wrapDict[set] = {'source': srcObj, 'target': members}
				
	return wrapDict


def mGetNodeOutputList(assetName):
	"""
	"""
	outNodeDict = {}
	setList = cmds.ls('*moGCNodeOut', r= 1, typ= 'objectSet')
	for set in _xList(setList):
		if ':' not in set or (':' in set and set.startswith(assetName)):
			outNodeDict = eval(cmds.getAttr(set + '.outNodeDict'))
				
	return outNodeDict
