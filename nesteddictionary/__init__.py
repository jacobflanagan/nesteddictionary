'''
A wrapper for python dicts. Derived from a need to search for keys in a nested dictionary.

Features:
- Uses keypaths in subscripting to navigate nested dictionaries ( ex: nested_dict[ ['path','to','key'] ] is the same as nested_dict['path']['to']['key'] )
- Adds functionality without violating any existing dict operations (that I know of); keypaths are in the form of a list which cannot be used as a key for a normal dict anyway.
- findall method: Finds all nested keys within a nested dictionary.
- get and set methods: Navigate using a keypath string with seperator ( ex: nested_dict.get('path.to.key') )
- insert method: create a full path to a nested key and set a value, even if the parent keys leading to the destination key don't already exist ( i.e., nested_dict.insert( ['new','path','to','key'], newval ) will add to the existing dictionay, resulting in: NestedDict({ 'path':{'to':{'key':val}}, 'newpath':{'to':{'key':newval}} }) ).
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

from functools import reduce
import operator

#User Exceptions
class KeypathError(Exception): pass #currently only used to track keypath errors durning _construct_path

class NestedDict:
    '''
    Nested dictionary is a wrapper for dict for key path navigation through subscriptablable means and methods for searching for nested keys. Works with mixed nested dictionaries (lists and dicts). Useful for JSON formatted request returns.
 
    Key Terms:
     - keypath: Key path a list of keys that make up the path to a destination in a nested dictionary.
     - Destination key: The last key in a key path.

    Caveats:
     - JSON dumps cannot be done directly. Either unnest (i.e.,: nested_dict.unnest()) before calling dumps or use the built in dumps methdod (ex: nested_dict.dumps())
     - If setting an int as a new destination key, it is assumed to be a dictionary key and not a list index. If inserting a list using an index is desired, the list must first be set as a value at the parent level. It can then be indexed, but only at the list's length at most (use the len function for a nested list and its value to insert a new obj in the list, or just use append).
     - This is a tool to make accessing a dictionary easier to program, especially requests results (like from AWS). This is slower then accessing a regular dictionary the usual way (which is probably why something simialar hasn't been implemented already). Use at your own lesiure.

    Scriptability:
     - Use as a normal dict (i.e., d["key"])
     - Use keypath; a list of keys, i.e., nested_dict[["path","to","key"]] which is the same as nested_dict["path"]["to"]["key"] in normal dictionaries
    
    Methods:
     - findall: Finds all key paths, returned in a list; key paths are represented by a list (ex: ["path","to","key"]). Example return: [ ['path','to','key'], ['another_path','to','key'] ].
     - findall_kv (key/value): Finds all key paths and their values stored in a dictionary, returns in a list; Key/value dictionary has 2 keys: 'keypath' and 'value'. keypath is a key path list and value is the child of this keypath. If values are frequently accessed using a search, it may be more efficient to get at the value using this function. Example return: [ { 'keypath':['path','to','key'], 'value': } ]
 
    
    NOTE: For keypaths, a tuple is simplier than a list, however, tuples can be real keys for a normal dictionary and this interfers with this behavior.
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
    def _construct_path(self, keypath: list, d: Union[dict,list]) -> None:
        '''
        Travels down existing path or constructs it using keypath map.
        Warning: keypath parameter gets destroyed.
        '''
        if keypath:
            key = keypath[0]
            if isinstance(d,dict):
                if key not in d.keys():
                    d[key] = {}
                return self._construct_path(keypath[1:], d[key])
            else: #d was a list
                try:
                    if key == len(d): #if consecutive index given, append a new dictionary for a new list
                        d.append({}) #append an empty list
                    return self._construct_path(keypath[1:], d[key])
                except IndexError as e:
                    raise IndexError(f'[{key}] IndexError: {e}')
                except TypeError as e:
                    raise TypeError(f'[{key}] TypeError: {e}')
                except KeypathError as e:
                    raise KeypathError(f'[{key}]{e}')
            return self._construct_path(keypath[1:], d[key])
        
        #base case: empty list, return none
        return None

    def _traverse( self, keypath, construct_path = False ):
        '''
        Traverse a dictionary with a given key path. 
        While faster than recursion, the functools.reduce method doesn't allow for tracking along keys the way nesteddict_v1.1.0 had (which was useful for debugging).

        param list keypath: The key path; either a single key or a list of keys.
        '''
        if construct_path:
            self._construct_path( keypath, self._data )

        if isinstance(keypath, list):
            return reduce(operator.getitem, keypath, self._data)
        else:
            return self._data[keypath]


    def __bool__(self) -> bool:
        return bool(self._data)

    def __eq__(self, other: Any) -> bool:
        return self._data == other

    def unnest( self ):
        return self._data

    @classmethod
    def _nestize( cls, d ):
        '''
        Returns d as NestedDict if a dictionary or a list. Else returns original d back
        '''
        if isinstance(d,(dict,list)):
            return cls( d )
        else:
            return d

    def __getitem__( self, keypath ):
        '''
        Returns a NestedDict of value if a dict or list. Otherwise just returns the value.
        '''
        item = self._traverse(keypath)
        return self._nestize( item )

    def _cast_index(self, item):
        '''
        Tries to cast item into an int, otherwise returns the original item. Used with parsing a keypath_str.
        '''
        try:
            return int(item)
        except ValueError:      #assume item wasn't meant to be an integer and return
            return item

    def get(self, keypath_str:str, sep:str = '.'):
        '''
        Get value using a string with a seperator. Default seperator is a dot, but this can be changed using the sep parameter.

        NOTE: Integer-like keys will be treated as an integers. If the key needs to be a string representation of an integer, encase it with quotes (i.e., use ", ', \" or \')

        param str keypath_str: keypath represented by a string with seperators defined by sep
        param str sep: seperator used for parsing keypath_str
        '''
        keypath = [self._cast_index(item) for item in keypath_str.split(sep)]
        return self.__getitem__(keypath)

    def __iter__(self) -> Iterator:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __ne__(self, other: Any) -> bool:
        return self._data != other

    def __setitem__( self, keypath, value ) -> None: 

        if isinstance(keypath,list):
            journeykeys, destinationkey = keypath[:-1], keypath[-1]
            self._traverse(journeykeys)[destinationkey] = value
        else:
            self._data[keypath] = value

        return None
    
    def set( self, keypath_str:str, value, sep:str = '.' ) -> None:
        '''
        Set value using a string with a seperator. Default seperator is a dot, but this can be changed using the sep parameter.

        NOTE: Integer-like keys will be treated as integers. If the key needs to be a string representation of an integer, encase it with quotes (i.e., use ", ', \" or \')

        param str keypath_str: keypath represented by a string with seperators defined by sep
        param value: value to be set at keypath
        param str sep: seperator used for parsing keypath_str
        '''
        keypath = [self._cast_index(item) for item in keypath_str.split(sep)]
        self.__setitem__(keypath, value)

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
        if isinstance(self._data,list): #if a list, give all possible indecies of a list
            return list( range( len(self._data) ) )
        return self._data.keys()

    def dumps(self, *args, **kwargs):
        '''
        Shortcut to json.dumps for the underlying dictionary. Same thing as json.dumps( nestd_dict.unnest() ) if nestd_dict were the NestedDict.
        See json.dumps for parameters.
        '''
        import json
        return json.dumps( self._data,*args, **kwargs)

    def insert(self, keypath: list, value, construct_path=True ) -> None: 
        '''
        Tries to insert a new value by constructing a path if it doesn't exist and inserting the value.
        '''
        journeykeys, destinationkey = keypath[:-1], keypath[-1]
        self._traverse( journeykeys, construct_path=True )[ destinationkey ] = value

    def findall(self, key) -> list:
        '''
        Finds matching keys within nested dictionary. Returns the list of keys to ALL found matches.
        NOTE: This returns a list of lists with the nested list being keypaths to a key (even if there is only a single result). 
        
        param key: Any valid dictionary key (usually str or int)

        TODO: Implement ability to search for subsets of a keypath (i.e., keypath = [])
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
        NOTE: This returns a list of lists with the nested list being keypaths to a key (even if there is only a single result).
        
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