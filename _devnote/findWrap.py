

from pymel.core import *


source = ls(sl= 1, typ= 'transform')[-1]
cList = source.getShape().connections(s= 0, p= 1, t= 'wrap')
print 'Source : ' + source.name()
print '-'*20
for c in cList:
	if c.longName().startswith('driverPoints'):
		print 'WrapNode : ' + c.nodeName()
		target = c.node().geomMatrix.connections()
		if target:
			print 'Target : ' + target[0].name()
			attrDict = {}
			for at in c.node().listAttr():
				if at.isKeyable():
					attrDict[str(at.longName())] = at.get()
			print attrDict
			#delete(c.node())

print '-'*20


listAttr('moGCWrap_1', ud= 1)

'''
falloffMode
exclusiveBind
autoWeightThreshold
weightThreshold
maxDistance

envelope
'''