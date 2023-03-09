# Nested Dictionary
**Version:** 1.2.2

A wrapper for python dicts that allows you to search and navigate through nested dicts using **key paths**. Also works with mixed dictionaries (mixuture of nested lists and dicts). Derived from a need to search for keys in a nested dictionary; too much time was spent on building yet another full class for nested dictionaries, but it suited our needs.

*Quick Start Example:*
```python
>>> from nesteddictionary import NestedDict     #import the NestedDict class
>>> d = {'path':{'to':{'key':'val'}}}           #normal way of doing nested dictionary
>>> nested_dict = NestedDict( d )               #created a nested dictionary from a normal dictionary
```

**Features**:
- Uses keypaths in subscripting to navigate nested dictionaries ( ex: ```nested_dict[ ['path','to','key'] ]``` which is the same as ```nested_dict['path']['to']['key']``` )
- Adds functionality without violating any existing dict operations (that I know of); keypaths are in the form of a list which cannot be used as a key for a normal dict anyway. All other dict rules still apply.
- findall method: Finds all nested keys within a nested dictionary.
- get and set methods: Navigate using a keypath string with seperator ( ex: ```nested_dict.get('path.to.key')``` )
- insert method: create a full path to a nested key and set a value, even if the parent keys leading to the destination key don't already exist ( i.e., ```nested_dict.insert( ['newpath','to','key'], 'newval'``` ) will add to the existing dictionay, resulting in: ```NestedDict({ 'path':{'to':{'key':'val'}}, 'newpath':{'to':{'key':'newval'}} })``` ).

Limitations:
- While fast, it adds some overhead and therefore cannot ever be as fast as accessing dicts the regular way.

Changes (PEP 440: major.minor.patch):
- v0.1.0: Developed methods for searching keys in nested dictionaries.
- v1.0.1: Initial working version of the nesteddictionary class.
- v1.2.0: Changed dictionary traversing from recursive to functools.reduce; This is less pythonic yet faster (however, still not nearly as fast as directly accessing dicts and list).
- v1.2.2: Minor patch - removes a debugging print statement in the get method.
    
For comparison, when doing (these are not included in tests, but are easy enough to write and test on your own):
  ```python
  >>> d = [{1:{2:'value'}}]   
  >>> %timeit using_reduce(d,[0,1,2])     #reduce from functools
  >>> %timeit using_recursion(d,[0,1,2])  #what was used in v1, more pythonic
  >>> %timeit d[0][1][2]                  #direct access; fastest
  ```
  Yields:
  ```python
  >>> 648 ns ± 3.17 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)    #reduce
  >>> 1.77 µs ± 4.05 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)   #recursion
  >>> 89.3 ns ± 0.448 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each) #direct
  ```

References:
- [Scalpl](https://github.com/ducdetronquito/scalpl/): A similar implementation to nested dictionaries. Some good methodology here.
- [Functools Reduce for dicts](https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys): Speed up dictionary acces, but non-pythonic.
- Others I'm sure I forgot to mention. Thank you.