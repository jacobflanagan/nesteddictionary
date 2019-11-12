# Nested Dictionary
A wrapper for python dicts. Also works with mixed dictionaries (mixuture of nested lists and dicts). Derived from a need to search for keys in a nested dictionary, so too much time was spent on building yet another full class for nested dictionaries. Some testing was performed for bugs and efficiency...

Benefits:
- Uses keypaths in subscripting to navigate nested dictionaries ( ex: nested_dict['path']['to']['key'] is the same as nested_dict[ ['path','to','key'] ] )
- Adds functionality without violating any existing dict operations (that I know of); keypaths are in the form of a list which cannot be used as a key for a normal dict anyway.
- findall method: Finds all nested keys within a nested dictionary.
- get and set methods: Navigate using a keypath string with seperator ( ex: nested_dict.get('path.to.key') )
- insert method: create a full path to a nested key and set a value, even if the parent keys leading to the destination key don't already exist ( i.e., nested_dict.insert( ['new','path','to','key'], newval ) will add to the existing dictionay, resulting in: NestedDict({ 'path':{'to':{'key':val}}, 'newpath':{'to':{'key':newval}} }) ).

Changes (PEP 440: major.minor.path):
- v1.0.1: Initial working version of nesteddictionary.
- v1.2.0: Changed dictionary traversing from recursive to functools.reduce; it's less pythonic but faster (yet, still not nearly as fast as directly accessing dicts and list). For comparison, when doing:
    > d = [{1:{2:'value'}}]   
    > %timeit using_reduce(d,[0,1,2])    #reduce from functools
    > %timeit using_recursion(d,[0,1,2]) #what is used in v1, considered more pythonic
    > %timeit d[0][1][2]                 #direct access
  Yields:
    > reduce:    648 ns ± 3.17 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
    > recursion: 1.77 µs ± 4.05 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
    > direct:    89.3 ns ± 0.448 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

References: 
- https://github.com/ducdetronquito/scalpl/ : A similar implementation to nested dictionaries. Pulled some methodology ideas from here.
- https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys : Speed up dictionary acces but non-pythonic.