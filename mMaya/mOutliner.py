# -*- coding:utf-8 -*-
'''
Created on 2016.04.28

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import os, sys
import functools
from .. import mLogger; reload(mLogger)
exc = os.path.basename(sys.executable)
logger = mLogger.MLog('moGC.mMaya.outline',
					False if exc == 'mayapy.exe' else True)



def _useSelection(func):
	"""
	"""
	@functools.wraps(func)
	def getSele(*arg, **kwarg):
		logger.debug('arg, kwarg: ' + str(arg) + str(kwarg))
		result = []
		if not arg:
			logger.debug('No designation, use selection.')
			nodes = cmds.ls(sl= 1, l= 1)
			if nodes:
				for node in nodes:
					if func(node):
						result.extend(func(node))
			else:
				logger.warning('No designation, and no selection.')
		else:
			logger.debug('Have designation, execute.')
			if func(arg):
				result.extend(func(arg))

		return result

	return getSele


def findRoot(nodeType= None):
	"""
	找出所有已選取物件在 outliner 裡各自的根物件。
	@param nodeType: [list, string] 根物件型別。要找多種型別可用 list，
					只找單型別可用 string 。
	"""
	if nodeType is None:
		nodeType = []
	rootNodes = []
	seleList = cmds.ls(sl= 1, type= nodeType, l= 1)
	if seleList:
		for obj in seleList:
			root = obj.split('|')[1]
			if root not in rootNodes:
				if cmds.objectType(root) in nodeType or nodeType == []:
					rootNodes.append(root)
	else:
		logger.warning('No designation, and no selection.')

	return rootNodes

@_useSelection
def findHidden(node= None):
	"""
	列出選取物件或指定物件底下隱藏的子物件。
	@param node: [string] 物件名稱
	"""
	hiddenObj = []
	allChild = cmds.listRelatives(node, ad= 1, f= 1)
	for child in allChild:
		if cmds.attributeQuery('visibility', ex= 1, node = child):
			if not cmds.getAttr(child + '.visibility'):
				hiddenObj.append(child)
	return hiddenObj


def findType(nodeType, excludeType= None, node= None):
	"""
	列出選取物件或指定物件底下的特定型別子物件，
	或者，
	列出選取物件或指定物件底下特定型別之外的子物件
	@param nodeType: [string] 物件型別
	@param excludeType: [bool] include or exclude 預設為 False
	@param node: [string] 物件名稱
	"""
	if excludeType is None:
		excludeType = False
	@_useSelection
	def doFind(node):
		typObj = []
		allChild = cmds.listRelatives(node, ad= 1, f= 1)
		for child in allChild:
			if excludeType - (cmds.objectType(child) in nodeType):
				typObj.append(child)
		return typObj

	if node is None:
		return doFind()
	else:
		return doFind(node)
	

@_useSelection
def findIMObj(node= None):
	"""
	"""
	IMObj = []
	dagList = cmds.listRelatives(node, ad= 1, f= 1)
	if dagList:
		for dag in dagList:
			if cmds.attributeQuery('intermediateObject', ex= 1, node = dag):
				if cmds.getAttr(dag + '.intermediateObject'):
					IMObj.append(dag)
	return IMObj

@_useSelection
def delEmpty(node= None):
	"""
	"""
	# a recursive function for remove empty transform 
	def removeEmptyTransform(dagList):
		for dag in dagList:
			if cmds.objExists(dag):
				dagParent = cmds.listRelatives(dag, p= 1, f= 1)
				dagChild = cmds.listRelatives(dag, c= 1, f= 1)
				if not dagChild:
					# this dag is empty, delete
					cmds.delete(dag)
					# check parent if it's empty after dag deleted
					removeEmptyTransform(dagParent)
	# remove empty transform
	allChild = cmds.listRelatives(node, ad= 1, f= 1, typ= 'transform')
	if allChild:
		removeEmptyTransform(allChild)



if __name__ == '__main__':
	pass