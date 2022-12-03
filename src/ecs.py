MAX_ENTITIES = 2**16
NULL_ENTITY = -1

# note on versions: since an id can be reused the version is also maintained to differentiate between ids
class entity_id:
    def __init__(self, identity, version):
        assert type(identity) == int
        assert type(version) == int
        self.identity = identity
        self.version = version

# note: this is a convenience wrapper class, this does not actually contain data
class entity:
    def __init__(self, e_id, system):
        assert type(e_id) == entity_id
        self.e_id = e_id
        self.system = system

    def add(self, name, item):
        self.system.component_add(name, self.e_id, item)

    def has(self, name):
        return self.system.component_has(name, self.e_id)

    def get(self, name):
        return self.system.component_get(name, self.e_id)

    def remove(self, name):
        return self.system.component_remove(name, self.e_id)

    def identity(self):
        return self.e_id.entity

    def version(self):
        return self.ed_id.version

# internal class for storing components
# contains a sparse and dense array
# the sparse array can be indexed with an id to check whether or not the entity contains the relevant component
# the index will contain another index into the dense array which stores the component
# this allows for efficient iteration, as well as fast lookup
class pool:
    def __init__(self, name, descriptor):
        self.name = name
        self.desc = descriptor
        self.sparse = [NULL_ENTITY] * MAX_ENTITIES
        self.dense = []
        self.components = []

    def clear(self):
        self.sparse = [NULL_ENTITY] * MAX_ENTITIES
        self.dense = []
        self.components = []

    def add(self, e, item):
        assert type(e) == int
        assert type(item) == self.desc
        assert self.sparse[e] == NULL_ENTITY
        self.sparse[e] = len(self.dense)
        self.dense.append(e)
        self.components.append(item)

    def get(self, e):
        assert type(e) == int
        assert not self.sparse[e] == NULL_ENTITY
        return self.components[self.sparse[e]]

    def remove(self, e):
        assert type(e) == int
        assert not self.sparse[e] == NULL_ENTITY
        i = self.sparse[e]
        j = len(self.dense) - 1
        self.sparse[e] = NULL_ENTITY
        self.sparse[self.dense[j]] = i
        self.dense[i] = j
        self.dense.pop()
        self.components[i] = self.components[j]
        return self.components.pop()

# implements ranged base looping for views
class view_iterator:
    def __init__(self, system, pool):
        self.system = system
        self.pool = pool
        self.idx = 0

    def __next__(self):
        if not self.idx < len(self.pool.dense):
            raise StopIteration
        e = self.pool.dense[self.idx]
        i = self.idx
        self.idx += 1
        return entity(self.system.entities[e], self.system), self.pool.components[i]

# helper class for the view iterator
class _view:
    def __init__(self, system, pool):
        self.system = system
        self.pool = pool

    def __iter__(self):
        return view_iterator(self.system, self.pool)

# implements ranged base looping for groups
class group_iterator:
    def __init__(self, system, group):
        self.system = system
        self.group = group
        self.idx = 0

    def __next__(self):
        if not self.idx < len(self.group.dense):
            raise StopIteration
        e = self.group.dense[self.idx]
        i = self.idx
        self.idx += 1
        return entity(self.system.entities[e], self.system), self.group.components[i].components()

# helper class for the group iterator
class _group:
    def __init__(self, system, group):
        self.system = system
        self.group = group

    def __iter__(self):
        return group_iterator(self.system, self.group)

# a class is used to encapsulate data and behaviour
# however to add additional attributes or behaviour to a class, it must be extended through inheritance or composition
# a component system seeks to solve this problem by separating attributes and behaviour into modularized components
# a system can be easily created through the composition of pre-defined attributes and behavirous, increasing code
# reuse
# additionally, systems can have attributes and behaviour dynamically added or removed
class component_system:
    def __init__(self):
        self.entities = []
        self.next_entity = NULL_ENTITY
        # all pools are associated with some integer, the bitset keeps track of which components an entity contains
        # note: probalbly not worth the extra memory usage, also limited to 64 pools at most
        self.entity_bitset = [0] * MAX_ENTITIES
        self.pools = []
        self.pool_id = {}
        self.groups = []
        self.group_id = {}

    def clear(self):
        for p in self.pools:
            p.clear()

        for g in self.groups:
            g.clear()

        self.entities = []
        self.next_entity = NULL_ENTITY
        self.entity_bitset = [0] * MAX_ENTITIES

    def entity_create(self):
        # we store entities no longer in use instead of deleting them
        # a linked list of these entities that are no longer in use is maintained internally, allowing them to be reused
        if not self.next_entity == NULL_ENTITY:
            temp_id = self.next_entity
            e_id = self.entities[temp_id]
            self.next_entity = e_id.identity
            e_id.identity = temp_id
            return entity(e_id, self)

        e_id = entity_id(len(self.entities), 0)
        self.entities.append(e_id)
        self.entity_bitset[e_id.identity] = 0
        return e_id

    def entity_destroy(self, e):
        e_id = self.entities[e.identity]

        # delete all associated components with the entity
        p_id = 0
        bitset = self.entity_bitset[e_id.identity]
        while bitset:
            if (bitset & (1 << p_id)):
                name = self.pools[p_id].name
                self.component_remove(name, e_id)
                bitset = bitset ^ (1 << p_id)
            p_id += 1

        e_id.version += 1
        temp_id = e_id.identity
        e_id.identity = self.next_entity
        self.next_entity = temp_id
        self.entity_bitset[e_id.identity] = 0

    # groups are a special type of component pool that allows for the efficient iteration over entities with a desired
    # set of components
    def group(self, name):
        assert name in self.group_id
        g_id = self.group_id[name]
        return _group(self, self.groups[g_id])

    # descriptor is a special component class that contains pointers to the desired group of components
    # constructor takes as input a dictionary with keys corresponding to the component names, and the value
    # being the component itself
    # descriptor must implement:
    # pools() which returns a list of the desired component names
    # components() which returns a tuple of its components
    def group_create(self, name, descriptor):
        bitset = 0
        for component in descriptor.pools():
            assert component in self.pool_id
            p_id = self.pool_id[component]
            bitset = bitset | (1 << p_id)
        assert bitset not in self.group_id
        g_id = len(self.groups)
        self.group_id[bitset] = g_id
        self.group_id[name] = g_id
        self.groups.append(pool(name, descriptor))

    # views are used to iterate over a particular type of component
    def view(self, name):
        assert name in self.pool_id
        p_id = self.pool_id[name]
        return _view(self, self.pools[p_id])

    # components need to be registered before use due to internal behaviour
    def register(self, name, descriptor):
        assert name not in self.pool_id
        self.pool_id[name] = len(self.pools)
        self.pools.append(pool(name, descriptor))

    def component_add(self, name, e, item):
        assert name in self.pool_id
        p_id = self.pool_id[name]
        pool = self.pools[p_id]
        pool.add(e.identity, item)
        bitset = self.entity_bitset[e.identity]
        bitset = bitset | (1 << p_id)
        self.entity_bitset[e.identity] = bitset
        self.group_add(bitset, e)

        # components can register a callback that will be called once they are added to an entity
        item.component_callback(entity(e, self))

    def component_has(self, name, e):
        assert name in self.pool_id
        bitset = self.entity_bitset[e.identity]
        p_id = self.pool_id[name]
        return ((bitset & (1 << p_id)) == (1 << p_id))

    def component_get(self, name, e):
        assert name in self.pool_id
        pool = self.pools[self.pool_id[name]]
        return pool.get(e.identity)

    def component_remove(self, name, e):
        assert name in self.pool_id
        bitset = self.entity_bitset[e.identity]
        if bitset in self.group_id:
            self.group_remove(bitset, e)
        p_id = self.pool_id[name]
        pool = self.pools[p_id]
        pool.remove(e.identity)
        bitset = bitset ^ (1 << p_id)
        self.entity_bitset[e.identity] = bitset

    # internal function that checks if the entity should be added to a registered group
    def group_add(self, bitset, e):
        found = False
        bits = None
        # find out if the entity should be added to a group
        for b in self.group_id.keys():
            if type(b) == str:
                continue
            if b & bitset == b:
                found = True
                bits = b
                break

        if not found:
            return
        group = self.groups[self.group_id[bits]]
        if group.sparse[e.identity] != NULL_ENTITY:
            return # return if the entity is already part of a group, note: corner cases WILL occur

        p_id = 0
        components = {}
        temp = bits
        # get all components to add
        while temp:
            if (temp & (1 << p_id)):
                pool = self.pools[p_id]
                components[pool.name] = pool.get(e.identity)
                temp = temp ^ (1 << p_id)
            p_id += 1
        group.add(e.identity, group.desc(components))

    def group_remove(self, bitset, e):
        group = self.groups[self.group_id[bitset]]
        group.remove(e.identity)
