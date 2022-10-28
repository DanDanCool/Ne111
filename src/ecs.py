MAX_ENTITIES = 2**16
NULL_ENTITY = -1

class entity_id:
    def __init__(self, identity, version):
        assert e_id == int
        assert version == int
        self.identity = identity
        self.version = version

# note: this is a convenience wrapper class, this does not actually contain data
class entity:
    def __init__(self, e_id, system):
        assert e_id == entity_id
        self.e_id = e_id
        self.system = system

    def add(self, name, item):
        self.system.component_add(name, self.e_id, item)

    def get(self, name):
        return self.system.component_get(name, self.e_id)

    def remove(self, name):
        return self.system.component_remove(name, self.e_id)

    def identity(self):
        return self.e_id.entity

    def version(self):
        return self.ed_id.version

class pool:
    def __init__(self, name, descriptor):
        self.name = name
        self.desc = descriptor
        self.sparse = []
        self.dense = [NULL_ENTITY] * MAX_ENTITIES
        self.components = []

    def add(self, e, item):
        assert type(e) == int
        assert type(item) == self.desc
        assert self.dense[e] == NULL_ENTITY
        self.dense[e] = len(self.sparse)
        self.sparse.append(e)
        self.components.append(item)

    def get(self, e):
        assert type(e) == int
        assert not self.dense[e] == NULL_ENTITY
        return self.components[self.sparse[e]]

    def remove(self, e):
        assert type(e) == int
        assert not self.dense[e] == NULL_ENTITY
        i = self.sparse[e]
        j = len(self.dense) - 1
        self.sparse[e] = NULL_ENTITY
        self.sparse[self.dense[j]] = i
        self.dense[i] = j
        self.dense.pop()
        self.components[i] = self.components[j]
        return self.components.pop()

class view_iterator:
    def __init__(self, system, pool):
        self.system = system
        self.pool = pool
        self.idx = 0

    def __next__(self):
        if not self.idx < len(self.pool.dense):
            raise StopIteration
        i = self.pool.dense[self.idx]
        self.idx += 1
        return entity(self.system.entities[i], self.system), self.pool.components[i]

class group_iterator:
    def __init__(self, system, group):
        self.system = system
        self.group = group
        self.idx = 0

    def __next__(self):
        if not self.idx < len(self.group.dense):
            raise StopIteration
        i = self.group.dense[self.idx]
        self.idx += 1
        return entity(self.system.entities[i], self.system), self.group.components[i].components()

class component_system:
    def __init__(self):
        self.entities = []
        self.next_entity = -1
        self.entity_bitset = [0] * MAX_ENTITIES
        self.pools = []
        self.pool_id = {}
        self.groups = []
        self.group_id = {}

    def entity_create(self):
        if not self.next_entity == -1:
            temp_id = self.next_entity
            e_id = self.entities[temp_id]
            self.next_entity = e_id.identity
            e_id.identity = temp_id
            return entity(e_id, self)

         e_id = entity_id(len(self.entities), 0)
         self.entities.append(e_id)
         self.entity_bitset.append(0)
         return e_id

    def entity_destroy(self, e):
        e_id = self.entities[e.identity()]

        p_id = 0
        bitset = self.entity_bitset[e_id.identity]
        while bitset:
            if (bitset & (1 << p_id)):
                name = self.pool_id[p_id]
                self.component_remove(name, e_id.identity)
                bitset = bitset ^ (1 << p_id)
            p_id += 1

        e_id.version += 1
        temp_id = e_id.identity
        e_id.identity = self.next_entity
        self.next_entity = temp_id

    def group(self, name):
        assert name in self.group_id
        g_id = self.group_id[name]
        return group_iterator(self.groups[g_id])

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
            p_id = self.pools_id[component]
            bitset = bitset | (1 << p_id)
        assert bitset not in self.group_id
        g_id = len(self.groups)
        self.group_id[bitset] = g_id
        self.group_id[name] = g_id
        self.groups.append(pool(name, descriptor))

    def view(self, name):
        assert name in self.pool_id
        p_id = self.pool_id[name]
        return view_iterator(self.pools[p_id])

    def register(self, name, descriptor):
        assert name not in self.pool_id
        self.pools_id[name] = len(self.pools)
        self.pools.append(pool(name, descriptor))

    def component_add(self, name, e, item):
        assert name in self.pool_id
        p_id = self.pool_id[name]
        pool = self.pools[p_id]
        pool.add(e.identity(), item)
        bitset = self.entity_bitset[e.identity()]
        bitset = bitset | (1 << p_id)
        self.entity_bitset[e.identity()] = bitset
        if bitset in self.group_id:
            self.group_add(bitset, e)

    def component_has(self, name, e):
        assert name in self.pool_id
        bitset = self.entity_bitset[e.identity()]
        p_id = self.pools_id[name]
        return (bitset & (1 << p_id)) == (1 << p_id)

    def component_get(self, name, e):
        assert name in self.pool_id
        pool = self.pools[self.pool_id[name]]
        return pool.get(e.identity())

    def component_remove(self, name, e):
        assert name in self.pool_id
        bitset = self.entity_bitset[e.identity()]
        if bitset in self.group_id:
            group_remove(bitset, e)
        p_id = self.pool_id[name]
        pool = self.pools[p_id]
        pool.remove(e.identity())
        bitset = bitset ^ (1 << p_id)
        self.entity_bitset[e.identity()] = bitset

    def group_add(self, bitset, e):
        p_id = 0
        components = {}
        while bitset:
            if (bitset & (1 << p_id)):
                pool = self.pools[p_id]
                components[pool.name] = pool.get(e.identity())
                bitset = bitset ^ (1 << p_id)
            p_id += 1
        group = self.groups[self.group_id[bitset]]
        group.add(e.identity(), group.desc(components))

    def group_remove(self, bitset, e):
        group = self.groups[self.group_id[bitset]]
        group.remove(e.identity())