'''
Wrapper for dict. 
Inspirational References: 
 - https://github.com/ducdetronquito/scalpl/
 - https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys : Speed up dictionary acces but non-pythonic
'''

from typing import (
    Any,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Optional,
    Type,
    TypeVar,
    ValuesView,
    Union
)

#User Exceptions
class KeypathError(Exception): pass

class NestedDict:
    '''
    Nested dictionary is a wrapper for dict for key path navigation through subscriptablable means and methods for searching for nested keys. Useful for JSON formatted request returns.
 
    Key Terms:
     - keypath: Key path a list of keys that make up the path to a destination in a nested dictionary.
     - Destination key: The last key in a key path.

    Caveats:
     - JSON dumps cannot be done directly. Either unnest (i.e.,: nested_dict.unnest()) before calling dumps or use the built in dumps methdod (ex: nested_dict.dumps())
     - If setting an int as a new destination key, it is assumed to be a dictionary key and not a list index. If inserting a list using an index is desired, the list must first be set as a value at the parent level. It can then be indexed, but only at the list's length at most (use the len function for a nested list and its value to insert a new obj in the list, or just use append).
     - This is a tool to make accessing a dictionary easier to program, especially requests results (like from AWS). This is slower then accessing a regular dictionary the usual way (which is probably why something simialar hasn't been implemented already). Use at your own lesiure.

    Scriptable: 
     - Use as a normal dict (i.e., d["key"])
     - Use keypath; a list of keys, i.e., nested_dict[["path","to","key"]] which is the same as nested_dict["path"]["to"]["key"] in normal dictionaries
    
    Methods:
     - findall: Finds all key paths, returned in a list; key paths are represented by a list (ex: ["path","to","key"]). Example return: [ ['path','to','key'], ['another_path','to','key'] ].
     - findall_kv (key/value): Finds all key paths and their values stored in a dictionary, returns in a list; Key/value dictionary has 2 keys: 'keypath' and 'value'. keypath is a key path list and value is the child of this keypath. If values are frequently accessed using a search, it may be more efficient to get at the value using this function. Example return: [ { 'keypath':['path','to','key'], 'value': } ]
 
    
    Note-to-self: For keypaths, a tuple is simplier than a list, however, tuples can be real keys for a normal dictionary and this interfers with this behavior.
    '''

    __slots__ = ("_data","_datatype") #self variables must be listed here

    def __init__( self, data: Optional[dict] = None ) -> None:
        '''
        Initializes class with a given dictionary or list. If None is given, initializes with a new dictionary.

        Exceptions:
         - TypeError: A type other than dict, list or None was given for data. 
        '''
        if data and not isinstance(data,(dict,list)):
            raise TypeError("Only dict or list can be a nested dictionary.")

        self._data = data or {}              #sets data or initializes an empty dict
        self._datatype = type(self._data)
        return None

    #private functions
    def _traverse( self, keypath: list, d: Optional[dict] = None, addmissingkeys = False ): #TODO: utilize addmissingkeys then reuse in the insert method.
        '''
        Traverse a dictionary with a given a key path.

        param list keypath: The key path.
        param Union[dict,list] d: dictionary to traverse (if nothing given, will use self._data)

        Exceptions:
         - IndexError, TypeError: A key higher than the length of a list for wrong type was given for a key of a list.
         - KeyError: A key given that doesn't exist within a dict.
         - KeypathError: User exception allowing recursive errors to iterate back through.
        '''
        d = d or self._data
        try:
            if len(keypath) > 1:
                nextstop, remainingpath = keypath[0], keypath[1:]
                return self._traverse( remainingpath, d[nextstop] )
            else:
                return d[keypath[0]]
        except (TypeError,IndexError) as e:
            raise KeypathError(f"[{keypath[0]}] (list:IndexError)")
        except KeypathError as e:
            raise KeypathError(f"[{keypath[0]}]{e}")
        except KeyError as e:
            raise KeypathError(f"[{keypath[0]}] (dict:KeyError)")

    def __bool__(self) -> bool:
        return bool(self._data)

    def __eq__(self, other: Any) -> bool:
        return self._data == other

    def unnest( self ):
        return self._data

    @classmethod
    def _nestize( cls, d ):
        '''
        NestedDict from dictionary or list. If something else, returns param d back.
        '''
        try:
            return cls( d )
        except TypeError:
            return d

    def __getitem__( self, keypath ):
        '''
        Returns a NestedDict of the child if a dict or list. Otherwise returns value.
        '''
        try:
            if isinstance(keypath, list):                       #lists are assumed a keypath
                return self._nestize( self._traverse( keypath ) )    #return as a NestedDict
            else:
                try:
                    return self._nestize( self._data[keypath] )  #When nestizing -> NestedDict, only dicts and lists are accepted, otherwise a TypeError is raised. Subscripting most other classes also throws this error.
                except TypeError:                               #Some value found, return it
                    return self._data[keypath]
        except (TypeError, KeyError, IndexError) as e:
            raise KeyError(f"{keypath}: doesn't exist ({e})")
        except KeypathError as e:
            raise KeypathError(f"{keypath} halted at: {e}")

    def __iter__(self) -> Iterator:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __ne__(self, other: Any) -> bool:
        return self._data != other

    def __setitem__( self, keypath, value ) -> None: 
        logger = logging.getLogger()
        if isinstance( value, dict ):
            value = NestedDict(value)               #keep new nested dictionaries consistent
        #try:
        if isinstance(keypath, list):
            destination = keypath.pop()
            path = keypath
            self._traverse( keypath=path )[destination] = value
        else:
            self._data[keypath] = value
        #except Exception as e:
        #    raise Exception(e)

    def __str__(self) -> str:
        #return f"{str(self._data)}"
        return f"{__class__.__name__}({str(self._data)})"
    
    def __repr__(self):
        #return f"{str(self._data)}"
        return f"{__class__.__name__}({str(self._data)})"

    def clear(self) -> None:
        return self._data.clear()

    def copy(self) -> dict:
        return self._data.copy()

    def keys(self):
        if isinstance(self._data,list):
            return list( range( len(self._data) ) )
        return self._data.keys()

    def dumps(self,indent=2) -> str:
        import json
        return json.dumps( self._data, indent=indent, sort_keys=True )

    def findall(self, key) -> list:
        '''
        Finds matching keys within nested dictionary. Returns the list of keys to all found keys. 
        BEWARE: All results, multiple or single, are returned as a list. Do not use the direct result as a path; iterate.
        
        param key: Any valid dictionary key (usually str or int)
        '''
        
        def findkeys(node, kv, nodepath = [] ):

            if isinstance(node, list):
                for ii, i in enumerate(node):
                    for x in findkeys(i, kv, nodepath + [ii]):
                        yield x

            elif isinstance(node, dict):
                if kv in node:
                    nodepath.append(kv)
                    yield nodepath
                for k, j in node.items():
                    for x in findkeys(j, kv, nodepath + [k]):
                        yield x
        
        return  list( findkeys(self._data, key) ) #cast generator to list

    def findall_kv(self, key) -> list:
        '''
        Just like findall, but with their values - this may speed up operations that require accessing values after finding a key. Returns list of dictionaries (i.e., [{}] ) that contain 2 whose keys are: 
         - keypath: list of keys that make up the key path.
         - value: The value (xml comparison, the "child") of the found key.
        BEWARE: All results, multiple or single, are returned as a list. Do not use the direct result as a path; iterate.
        
        param key: any valid dictionary key (usually str or int)
        '''
        def findkeys(node, kv, nodepath = [] ):

            if isinstance(node, list):
                for ii, i in enumerate(node):
                    for x in findkeys(i, kv, nodepath + [ii]):
                        yield x

            elif isinstance(node, dict):
                if kv in node:
                    nodepath.append(kv)
                    yield {"keypath":nodepath, "value":self._nestize(node[kv])}
                for k, j in node.items():
                    for x in findkeys(j, kv, nodepath + [k]):
                        yield x
        
        return  list( findkeys(self._data, key) ) #cast generator to list

    def insert(self, keypath: list, value, replace_dest = False) -> None: 
        '''
        Tries to insert a new value by constructing a path if it doesn't exist and inserting the value.
        '''
        
        def insert_recursively(data,keypath,value,replace):
            if len(keypath) > 1:
                try:
                    nextstop, remainingpath = keypath[0], keypath[1:]
                    insert_recursively(data[nextstop],remainingpath,value,replace)
                except (KeyError,TypeError):
                    data[nextstop] = {}
                    insert_recursively(data[nextstop],remainingpath,value,replace)
                except IndexError:              #There was a list, but the index given was outside
                    if nextstop == len(data): #Allow list append if the key given = len (increase by 1)
                        data.append({})
                        insert_recursively(data[nextstop],remainingpath,value,replace)
                    else:
                        raise IndexError(f"List index {nextstop} > len(list). Remaining path: {keypath} and value cannot be inserted.")
                #except TypeError
            else:
                try:
                    if replace or keypath[0] not in data.keys():
                        data[keypath[0]] = value
                    else:
                        raise Exception(f"An item already exists at keypath and replace_dest is set to False.")
                except IndexError:              #There was a list, but the index given was outside len of list
                    if nextstop == len(data):   #Allow list append if the key given = len (increase by 1)
                        data.append()
                        data[keypath[0]] = value
                    else:
                        raise IndexError(f"Index {keypath[0]} > len(list). Value cannot be inserted.")

        insert_recursively(self._data,keypath,value,replace_dest)


import logging
import time
FORMAT='[%(levelname)s] | %(asctime)s | %(name)15s.%(funcName)-15s |: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt=f'%Y-%m-%d %H:%M:%S {time.tzname[0]}')

logger = logging.getLogger()

root = [{"key0":{"key1":"value1",'key12':{"key3":"value"}}}]
# print( f"root is: {root}" )
nd = NestedDict( root )
# print( f"Keys: {nd.keys()}" )
nd[[0,"key0",'key1']] = 5
print( nd.findall_kv('key0') )
print( nd[0][['key0','key1']] )

nd.insert([1,'key1','key2'],30,True)
print( nd.dumps() )