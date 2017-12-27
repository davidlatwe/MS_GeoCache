# -*- coding:utf-8 -*-
'''
Created on 2016.07.06

@author: davidpower
'''
from pymel.core import *
import maya.cmds as cmds
from functools import partial
from subprocess import Popen, PIPE
import moGeoCache as moGeoCache; reload(moGeoCache)
import moGeoCacheUICmdExport as moGeoCacheUICmdExport; reload(moGeoCacheUICmdExport)
import os


def exec_getParams(*args):

	global rbtn_geoIO
	global txt_infoAssetName
	global txt_infoSceneName
	global textF_assetName
	global cBox_isPartial
	global cBox_isStatic
	global cBox_division
	global cBox_dupName
	global textF_filter
	global rbtn_execBy
	global rbtn_execDo

	mode = radioButtonGrp(rbtn_geoIO, q= 1, sl= 1)
	
	conflictList = str(textField(textF_filter, q= 1, tx= 1))
	if mode == 1:
		assetName_override = str(textField(textF_assetName, q= 1, tx= 1))
	if mode == 2:
		assetName_override = str(text(txt_infoAssetName, q= 1, l= 1))
	assetListStr = text(txt_infoAssetName, q= 1, l= 1)
	paramDict = {
		'assetName' : assetName_override if assetName_override else None,
		'sceneName' : str(text(txt_infoSceneName, q= 1, l= 1)),
		'isPartial' : checkBox(cBox_isPartial, q= 1, v= 1),
		 'isStatic' : checkBox(cBox_isStatic, q= 1, v= 1),
		   'subdiv' : 1 if checkBox(cBox_division, q= 1, v= 1) else None,
		 'sameName' : checkBox(cBox_dupName, q= 1, v= 1),
		 'conflict' : conflictList.split(';') if conflictList else [],
		'assetList' : [ast.strip() for ast in str(assetListStr).split(',')]
	}

	if exec_checkParam(paramDict):
		if mode == 1:
			actionType = radioButtonGrp(rbtn_execBy, q= 1, sl= 1)
			exec_Export(actionType, paramDict)
		if mode == 2:
			actionType = radioButtonGrp(rbtn_execDo, q= 1, sl= 1)
			exec_Import(actionType, paramDict)


def exec_checkParam(paramDict):
	"""
	"""
	paramList = [
		'assetName',
		'sceneName',
		'isPartial',
		 'isStatic',
		   'subdiv',
		 'sameName',
		 'conflict',
		'assetList'
	]

	for param in paramList:
		print param.rjust(10) + ' : ' + str(paramDict[param])
	return True

	
def exec_Export(actionType, paramDict):
	"""
	"""
	if actionType == 1:
		# ask file save if has modified
		if cmds.file(q= 1, mf= 1):
			msg = u'偵測到有場景更動未儲存。\n' \
				+ u'若不儲存的話，CMD 模式將不會讀取到變更。\n' \
				+ u'你要存檔嗎 ?'
			result = confirmDialog(t= u'不好意思', m= msg, b= [u'存', u'免', u'我想一下'],
				db= u'存', cb= u'免', ds= u'我想一下', icn= 'warning')
			if result == u'存':
				saveFile()
			if result == u'免':
				pass
			if result == u'我想一下':
				return
		pyFile = moGeoCacheUICmdExport.__file__
		projPath = workspace(q= 1, rd= 1)
		filePath = str(system.sceneName())
		assetList = str([dag.name() for dag in ls(sl= 1)])
		paramDict = str(paramDict)
		Popen(['mayapy', pyFile, projPath, filePath, assetList, paramDict], shell= False)
	if actionType == 2:
		moGeoCache.exportGeoCache(
			subdivLevel= paramDict['subdiv'],
			isPartial= paramDict['isPartial'],
			isStatic= paramDict['isStatic'],
			assetName_override= paramDict['assetName'],
			sceneName_override= paramDict['sceneName']
			)
	if actionType == 3:
		pass


def exec_Import(actionType, paramDict):
	"""
	"""
	if actionType == 1:
		moGeoCache.importGeoCache(
			sceneName= paramDict['sceneName'],
			isPartial= paramDict['isPartial'],
			assetName_override= paramDict['assetName'],
			ignorDuplicateName= paramDict['sameName'],
			conflictList= paramDict['conflict']
			)
	if actionType == 2:
		moGeoCache.gpuProxyReferencing(
			sceneName= paramDict['sceneName'],
			assetName_override= paramDict['assetName']
			)
	if actionType == 3:
		pass


def prep_SHDSet(mode, *args):
	"""
	"""
	sname = system.sceneName().namebase.lower()
	if '_shading_' not in sname and '_shd_' not in sname:
		msg = u'目前開啟的場景並不是一個 shading asseet。\n' \
			+ u'(此判斷是基於檔名未包含 "_shading_" 或 "_shd_" 等字串。)'
		confirmDialog(t= u'不可以', m= msg, b= [u'好，我錯了'], db= u'好，我錯了', icn= 'warning')
		return

	if mode == 'wrapSet':
		actSetName = 'moGCWrap'
		filt = ['mesh']
	if mode == 'smooth':
		filt = ['mesh']


	# deselect non-filt object
	objList = ls(sl= 1)
	for obj in objList:
		if (obj.nodeType() == 'transform' and obj.getShape().nodeType() not in filt)\
		or (obj.nodeType() != 'transform' and obj.nodeType() not in filt):
			select(obj, tgl= 1)
	# check if set exists
	objList = ls(sl= 1)

	if mode == 'wrapSet':
		if len(objList) > 1:
			# 將目前選取內容最後一個物件指定為 wrap source
			srcObj = objList[-1].name()
			# 列出目前已有的 wrap set
			actSet = ls(actSetName + '_*', typ= 'objectSet')
			if actSet:
				wsDict = {}
				# 整理出所有 wrap set 與其裡面的 wrap source
				for wSet in actSet:
					wsDict[getAttr(wSet + '.wrapSource')] = wSet
				# 若目前選取的 wrap source 已存在於現有的 wrap set
				# 就將目前選取的所有物件加進該 wrap set 並返回
				if srcObj in wsDict.keys():
					sets(wsDict[srcObj], add= objList)
					return

			# 目前選取的 wrap source 顯然並不存在於目前的 wrap set 中
			# 所以建立新的 wrap set
			wSet = sets(n= actSetName + '_1')
			# 紀錄當前的 wrap source
			addAttr(wSet, ln= 'wrapSource', dt= 'string')
			setAttr(wSet + '.wrapSource', srcObj)
		else:
			msg = u'嗯，請至少選取兩個物件，並注意選取順序。\n' \
				+ u'(先選取所有你要的 wrapTargets，最後再選一個 wrapSource。)'
			confirmDialog(t= u'噢，拜託喔', m= msg, b= [u'好，我錯了'], db= u'好，我錯了', icn= 'warning')

	if mode == 'smooth':
		for obj in objList:
			moGeoCache.doSmooth(obj.name(), 1)


def prep_RIGSet(mode, *args):
	"""
	"""
	sname = system.sceneName().namebase.lower()
	if '_rigging_' not in sname and '_rig_' not in sname and '_rm' not in sname and '_rsm' not in sname:
		msg = u'目前開啟的場景並不是一個 rigging asseet。\n' \
			+ u'(此判斷是基於檔名未包含 "_rigging_" 或 "_rig_" 或 "_rm" 等字串。)'
		confirmDialog(t= u'不可以', m= msg, b= [u'好，我錯了'], db= u'好，我錯了', icn= 'warning')
		return

	if mode == 'smoothSet':
		actSetName = 'moGCSmoothMask'
		filt = ['mesh']
	if mode == 'rigCtrlSet':
		actSetName = 'moGCRigCtrlExport'
		filt = ['nurbsCurve', 'locator']
	if mode == 'nodeOutSet':
		actSetName = 'moGCNodeOut'
		filt = ['mesh']

	if mode != 'nodeOutSet':
		# deselect non-filt object
		objList = ls(sl= 1)
		for obj in objList:
			if (obj.nodeType() == 'transform' and obj.getShape().nodeType() not in filt)\
			or (obj.nodeType() != 'transform' and obj.nodeType() not in filt):
				select(obj, tgl= 1)
		objList = ls(sl= 1)

	if mode == 'nodeOutSet':
		objList = []
		mChB =  uitypes.ChannelBox('mainChannelBox')
		ctrlList = mChB.getMainObjectList()
		attrList = mChB.getSelectedMainAttributes()
		if ctrlList:
			exec('dag = SCENE.' + ctrlList[0])
			objList = [dag]

	# check if set exists
	if objList:
		actSet = ls(actSetName, typ= 'objectSet')
		if actSet:
			if mode == 'nodeOutSet':
				nOutNodeDict = eval(actSet[0].outNodeDict.get())
			members = sets(actSet[0], q= 1, no= 1)
			for obj in objList:
				if obj.nodeType() != 'transform':
					obj = obj.getParent()
				if obj in members:
					# remove mesh
					sets(actSet[0], rm= obj)
					if mode == 'nodeOutSet':
						del nOutNodeDict[obj.name()]
						actSet[0].outNodeDict.set(str(nOutNodeDict))
				else:
					# add mesh
					sets(actSet[0], add= obj)
					if mode == 'nodeOutSet':
						nOutNodeDict[obj.name()] = attrList
						actSet[0].outNodeDict.set(str(nOutNodeDict))
		else:
			# create set and add mesh
			actSet = sets(n= actSetName)
			if mode == 'nodeOutSet':
				nOutNodeDict = { objList[0].name() : attrList }
				if not attributeQuery('outNodeDict', node= actSet, ex= 1):
					addAttr(actSet, ln= 'outNodeDict', dt= 'string')
				actSet.outNodeDict.set(str(nOutNodeDict))


def prep_setSmoothExclusive(*args):
	"""
	"""
	global cBox_exclusive
	sname = system.sceneName().namebase.lower()
	if '_rigging_' not in sname and '_rig_' not in sname and '_rm' not in sname and '_rsm' not in sname:
		msg = u'目前開啟的場景並不是一個 rigging asseet。\n' \
			+ u'(此判斷是基於檔名未包含 "_rigging_" 或 "_rig_" 或 "_rm" 等字串。)'
		confirmDialog(t= u'不可以', m= msg, b= [u'好，我錯了'], db= u'好，我錯了', icn= 'warning')
		checkBox(cBox_exclusive, e= 1, v= 0)
		return

	smoothSetName = 'moGCSmoothMask'

	smoothSet = ls(smoothSetName, typ= 'objectSet')
	if smoothSet:
		if not attributeQuery('smoothExclusive', node= smoothSet[0], ex= 1):
			addAttr(smoothSet[0], ln= 'smoothExclusive', at= 'bool')
		value = checkBox(cBox_exclusive, q= 1, v= 1)
		setAttr(smoothSet[0] + '.smoothExclusive', value)
	else:
		checkBox(cBox_exclusive, e= 1, v= 0)


def ui_getSmoothExclusive():
	"""
	"""
	global cBox_exclusive
	sname = system.sceneName().namebase.lower()
	if '_rigging_' not in sname and '_rig_' not in sname and '_rm' not in sname and '_rsm' not in sname:
		checkBox(cBox_exclusive, e= 1, v= 0)
		return

	smoothSetName = 'moGCSmoothMask'
	
	smoothSet = ls(smoothSetName, typ= 'objectSet')
	if smoothSet and attributeQuery('smoothExclusive', node= smoothSet[0], ex= 1):
		value = getAttr(smoothSet[0] + '.smoothExclusive')
		checkBox(cBox_exclusive, e= 1, v= 1)
	else:
		checkBox(cBox_exclusive, e= 1, v= 0)


def ui_getAssetName():
	"""
	"""
	global rbtn_geoIO

	if radioButtonGrp(rbtn_geoIO, q= 1, sl= 1) == 1:
		if ls(sl= 1):
			if not textField(textF_assetName, q= 1, tx= 1):
				assetList = moGeoCache.getAssetList()
				text(txt_infoAssetName, e= 1, l= ', '.join(assetList))
			else:
				warning('AssetName has override, only the last rootNode will be processed.')
				text(txt_infoAssetName, e= 1, l= textField(textF_assetName, q= 1, tx= 1))
		else:
			text(txt_infoAssetName, e= 1, l= '')


def ui_getSceneName():
	"""
	"""
	if not textField(textF_sceneName, q= 1, tx= 1):
		if radioButtonGrp(rbtn_geoIO, q= 1, sl= 1) == 1:
			sname = system.sceneName().namebase
			text(txt_infoSceneName, e= 1, l= sname)
		else:
			text(txt_infoSceneName, e= 1, l= '')
	else:
		text(txt_infoSceneName, e= 1, l= textField(textF_sceneName, q= 1, tx= 1))


def ui_initPrep(sideValue):
	"""
	"""
	global cBox_exclusive

	frameLayout(l= ' Preparation  -  S H D   R I G')
	columnLayout(adj= 1, rs= 4)
	if True:
		columnLayout(adj= 1)
		if True:
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_shd = text(l= 'S H D', al= 'center', fn= 'boldLabelFont', w= 40)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 3, adj= 2)
			if True:
				text(l= '', w= sideValue)
				btn_addWrapSet = button(l= 'Add Wrap Set', c= partial(prep_SHDSet, 'wrapSet'))
				text(l= '', w= sideValue)
				setParent('..')
			rowLayout(nc= 3, adj= 2)
			if True:
				text(l= '', w= sideValue)
				btn_exeMeshSmooth = button(l= 'Do Smooth', c= partial(prep_SHDSet, 'smooth'))
				text(l= '', w= sideValue)
				setParent('..')

		columnLayout(adj= 1)
		if True:
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_rig = text(l= 'R I G', al= 'center', fn= 'boldLabelFont', w= 40)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 2, adj= 2, h= 18)
			if True:
				text(l= '', w= sideValue)
				cBox_exclusive = checkBox(l= 'Make Smooth Set Excludsive', cc= prep_setSmoothExclusive)
				setParent('..')
			rowLayout(nc= 3, adj= 2)
			if True:
				text(l= '', w= sideValue)
				btn_makeSmoothSet = button(l= 'Model Smooth Set', c= partial(prep_RIGSet, 'smoothSet'))
				text(l= '', w= sideValue)
				setParent('..')
			#text(l= '', h= 5)
			rowLayout(nc= 3, adj= 2)
			if True:
				text(l= '', w= sideValue)
				btn_makeCurvesSet = button(l= 'Rigging Control Set', c= partial(prep_RIGSet, 'rigCtrlSet'))
				text(l= '', w= sideValue)
				setParent('..')
			#text(l= '', h= 5)
			rowLayout(nc= 3, adj= 2)
			if True:
				text(l= '', w= sideValue)
				btn_makeSpecKeyRig = button(l= 'Node Output Set', c= partial(prep_RIGSet, 'nodeOutSet'))
				text(l= '', w= sideValue)
				setParent('..')
			setParent('..')

		text(l= '', h= 5)

		setParent('..')
		setParent('..')


def ui_geoCache(midValue):
	"""
	"""
	global rbtn_geoIO
	global txt_infoAssetName
	global txt_infoSceneName
	global cBox_isPartial
	global cBox_isStatic
	global textF_assetName
	global cBox_division
	global textF_sceneName
	global menu_choose
	global cBox_dupName
	global textF_filter
	global rbtn_execBy
	global rbtn_execDo

	frameLayout(l= ' GeoCaching  -  A N I   S I M   G E O')
	columnLayout(adj= 1)
	if True:
		columnLayout(adj= 1)
		stuValue = 100
		if True:
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_sta = text(l= 'Status', al= 'center', fn= 'boldLabelFont', w= 40)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= 'Mode : ', al= 'right', w= stuValue)
				rbtn_geoIO = radioButtonGrp(nrb= 2, l='', cw3= [0, 70, 70],
					cl3= ['right', 'left', 'left'], la2= ['Export', 'Import'], sl= 1)
				setParent('..')
			text(l= '', h= 4)
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= 'Asset : ', al= 'right', w= stuValue)
				txt_infoAssetName = text(l= '', al= 'left')
				setParent('..')
			text(l= '', h= 3)
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= 'Scene : ', al= 'right', w= stuValue)
				txt_infoSceneName = text(l= '', al= 'left')
				setParent('..')
			setParent('..')

		columnLayout(adj= 1)
		if True:
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 5)
				tex_com = text(l= 'Common', al= 'center', fn= 'boldLabelFont', w= 50)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= '', w= midValue)
				cBox_isPartial = checkBox(l= 'Partial Export')
				setParent('..')
			row_textFAss = rowLayout(nc= 2, adj= 2)
			if True:
				text('Asset ', al= 'right', w= midValue)
				textF_assetName = textField(pht= 'assetName override')
				setParent('..')
			row_optnMAss = rowLayout(nc= 2, adj= 2, vis= 0)
			if True:
				text('Asset ', al= 'right', w= midValue)
				optnM_assetName = optionMenu(l= '')
				setParent('..')
			setParent('..')

		col_exp = columnLayout(adj= 1, vis= 1)
		if True:
			en = 1
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_exp = text(l= 'Export', al= 'center', fn= 'boldLabelFont', w= 40, en= en)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= '', w= midValue)
				cBox_isStatic = checkBox(l= 'Static Object')
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= '', w= midValue)
				cBox_division = checkBox(l= 'Division Smooth')
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				txt_sceneName = text('Scene ', al= 'right', w= midValue, en= en)
				textF_sceneName = textField(pht= 'sceneName override', en= en)
				setParent('..')
			text(l= '', h= 3)
			setParent('..')

		col_imp = columnLayout(adj= 1, vis= 0)
		if True:
			en = 1
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_com = text(l= 'Import', al= 'center', fn= 'boldLabelFont', w= 40, en= en)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 3, adj= 3)
			if True:
				txt_choose = text('', al= 'right', w= midValue - 20, en= en)
				icBtn_textF_choose = iconTextButton(i= 'fileOpen.png', w= 20, h= 20, en= en)
				textF_choose = textField(pht= 'scene geoCacheDir', en= en)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= '', w= midValue)
				cBox_dupName = checkBox(l= 'Duplicate Names', en= en)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				txt_filter = text('Filter Out ', al= 'right', w= midValue, en= en)
				textF_filter = textField(pht= 'string1;string2...', en= en)
				setParent('..')
			setParent('..')

		col_action = columnLayout(adj= 1)
		actValue = 50
		if True:
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_act = text(l= 'Action', al= 'center', fn= 'boldLabelFont', w= 40, en= 1)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			row_ExpAct = rowLayout(nc= 2, adj= 2)
			if True:
				text(l= 'By : ', al= 'right', w= actValue)
				rbtn_execBy = radioButtonGrp(nrb= 3, l='', cw4= [5, 55, 50, 60], h= 30,
					cl4= ['right', 'left', 'left', 'left'],
					la3= ['CMD', 'GUI', 'deadline'], sl= 1)
				setParent('..')
			row_ImpAct = rowLayout(nc= 2, adj= 2, vis= 0)
			if True:
				text(l= 'Do : ', al= 'right', w= actValue)
				rbtn_execDo = radioButtonGrp(nrb= 2, l='', cw3= [5, 55, 110], h= 30,
					cl3= ['right', 'left', 'left'],
					la2= ['GEO', 'GPU + Reference'], sl= 1)
				setParent('..')

			text(l= '', h= 5)
			setParent('..')
		button(l= 'Execute', h= 50, c= exec_getParams)

		setParent('..')
	setParent('..')

	# commands
	def getAssetListFromGeoRootDir():
		for c in optionMenu(optnM_assetName, q= 1, ill= 1):
			deleteUI(c)
		geoDir = moGeoCache.getGeoCacheRoot()
		if geoDir:
			isF = lambda d, f: os.path.isfile(os.path.join(d,f))
			dirList = [f for f in os.listdir(geoDir) if not isF(geoDir, f)]
			for d in dirList:
				menuItem(l= d, p= optnM_assetName)
			text(txt_infoAssetName, e= 1, l= dirList[0])

	def geoCacheIOctrlSwitch(col, vis, *args):
		layout(col, e= 1, vis= vis)
		if col == col_exp and vis:
			rowLayout(row_ExpAct, e= 1, vis= 1)
			rowLayout(row_ImpAct, e= 1, vis= 0)
			rowLayout(row_textFAss, e= 1, vis= 1)
			rowLayout(row_optnMAss, e= 1, vis= 0)
			checkBox(cBox_isPartial, e= 1, l= 'Partial Export')
			ui_getSceneName()
			ui_getAssetName()
		if col == col_imp and vis:
			rowLayout(row_ExpAct, e= 1, vis= 0)
			rowLayout(row_ImpAct, e= 1, vis= 1)
			rowLayout(row_textFAss, e= 1, vis= 0)
			rowLayout(row_optnMAss, e= 1, vis= 1)
			checkBox(cBox_isPartial, e= 1, l= 'Partial Import')
			text(txt_infoSceneName, e= 1, l= textField(textF_choose, q= 1, tx= 1))
			getAssetListFromGeoRootDir()

	radioButtonGrp(rbtn_geoIO, e= 1,
			of1= partial(geoCacheIOctrlSwitch, col_exp, 0),
			on1= partial(geoCacheIOctrlSwitch, col_exp, 1),
			of2= partial(geoCacheIOctrlSwitch, col_imp, 0),
			on2= partial(geoCacheIOctrlSwitch, col_imp, 1))

	def textFieldSync(source, target, *args):
		s = textField(source, q= 1, tx= 1)
		if s:
			text(target, e= 1, l= s)
		else:
			if str(textField(source, q= 1, pht= 1)).startswith('asset'):
				ui_getAssetName()
			if str(textField(source, q= 1, pht= 1)).startswith('scene'):
				ui_getSceneName()

	def optionMenuSync(source, target, *args):
		s = optionMenu(source, q= 1, v= 1)
		if s:
			text(target, e= 1, l= s)
		else:
			text(target, e= 1, l= '')

	textField(textF_assetName, e= 1, cc= partial(textFieldSync, textF_assetName, txt_infoAssetName))
	textField(textF_sceneName, e= 1, cc= partial(textFieldSync, textF_sceneName, txt_infoSceneName))
	textField(textF_choose, e= 1, cc= partial(textFieldSync, textF_choose, txt_infoSceneName))
	optionMenu(optnM_assetName, e= 1, cc= partial(optionMenuSync, optnM_assetName, txt_infoAssetName))

	def openCacheFolder(*args):
		assetName = text(txt_infoAssetName, q= 1, l= 1)
		msg = ''
		if assetName:
			assetName = [ast.strip() for ast in assetName.split(',')][-1]
			geoCacheRoot = moGeoCache.getGeoCacheRoot()
			geoCacheDir = geoCacheRoot + '/' + assetName
			if os.path.exists(geoCacheDir):
				result = fileDialog2(cap= 'geoCache Folder', fm= 3, okc= 'Select', dir= geoCacheDir)
				if result:
					folderName = os.path.basename(result[0])
					if os.path.exists(geoCacheDir + '/' + folderName):
						textField(textF_choose, e= 1, tx= folderName)
						text(txt_infoSceneName, e= 1, l= folderName)
					else:
						msg = u'這個 asset 並沒有你說的 geoCache 資料夾。'
			else:
				msg = u'唉。Asset [ ' + assetName + u' ] 並不存在於 moGeoCache 資料夾中，\n' \
					+ u'可能是從未輸出 GeoCache 過吧。'
		else:
			msg = u'請先選取或輸入一個 Asset，好嗎 ?'
		if msg:
			confirmDialog(t= u'警告你喔', m= msg, b= [u'好，我錯了'], db= u'好，我錯了', icn= 'warning')

	iconTextButton(icBtn_textF_choose, e= 1, c= openCacheFolder)


def ui_main():
	"""
	"""
	global windowName
	windowName = 'ms_GeoCache_uiMain'

	if window(windowName, q= 1, ex= 1):
		deleteUI(windowName)

	window(windowName, t= 'MS GeoCache_Tool', s= 0, mxb= 0, mnb= 0)
	main_column = columnLayout(adj= 1)
	# geoCache
	ui_initPrep(50)
	ui_geoCache(90)
	setParent('..')

	scriptJob(e= ['SelectionChanged', ui_getAssetName], p= windowName)
	scriptJob(e= ['PostSceneRead', ui_getSceneName], p= windowName)
	scriptJob(e= ['SceneSaved', ui_getSceneName], p= windowName)
	scriptJob(e= ['PostSceneRead', ui_getSmoothExclusive], p= windowName)
	ui_getAssetName()
	ui_getSceneName()
	ui_getSmoothExclusive()

	#cmds.window('ms_GeoCache_uiMain', q= 1, h= 1)
	window(windowName, e= 1, h= 531, w= 270)
	showWindow(windowName)
