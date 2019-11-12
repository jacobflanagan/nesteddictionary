import sys
import os

sys.path.insert( 0, os.path.join(sys.path[0],"..") )

from nesteddictionary import NestedDict

#basic mixed nested dictionary
nested_dict = [ { "key0":{ "key1":"value1", 'key12':{ "key3":"value"} } } ]

#Create a NestedDict from a normal dictionary
nd = NestedDict( nested_dict )

#Example keypath and setting value at keypath
keypath = [0,'key0',3]
nd[keypath] = 5

#Find all key destinations of 3 and return keypath and value (kv = keypath/value)
print( "\nKeypaths and values containing 3:\n", nd.findall_kv(3) )

#insert
nd.insert( [1,'newkey'], 'newval' )

#Example of a JSON dumps
print( "\nJSON dumps:\n", nd.dumps( indent=2 ) )