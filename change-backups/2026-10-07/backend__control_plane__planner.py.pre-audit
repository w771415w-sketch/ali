from __future__
from collections import defaultdict, deque
from .schemas import Task, new_id
class DependencyError(ValueError): pass
class Planner:
    def build(self, contract):
        tasks=[]
        if contract.platform or contract.features:
            tasks.append(Task(new_id("task"),"Analyze repository/project context",priority=95))
            tasks.append(Task(new_id("task"),"Finalize requirements and acceptance criteria",priority=92,depends_on=[tasks[-1].id]))
            tasks.append(Task(new_id("task"),"Design architecture",priority=85,depends_on=[tasks[-1].id]))
            prev=tasks[-1].id
            if "Database" in contract.features or any(x in contract.features for x in ["Inventory","Sales","Purchases","Products"]):
                tasks.append(Task(new_id("task"),"Implement database/data layer",priority=82,depends_on=[prev])); prev=tasks[-1].id
            tasks.append(Task(new_id("task"),"Implement backend/business logic",priority=78,depends_on=[prev])); prev=tasks[-1].id
            tasks.append(Task(new_id("task"),"Implement user interface",priority=70,depends_on=[prev])); prev=tasks[-1].id
            tasks.append(Task(new_id("task"),"Run unit/integration tests",priority=65,depends_on=[prev],parallelizable=True)); prev=tasks[-1].id
            tasks.append(Task(new_id("task"),"Run acceptance and regression checks",priority=60,depends_on=[prev])); prev=tasks[-1].id
            tasks.append(Task(new_id("task"),"Build and package",priority=55,depends_on=[prev])); tasks.append(Task(new_id("task"),"Document and deliver",priority=45,depends_on=[tasks[-1].id]))
        else: tasks.append(Task(new_id("task"),"Clarify and answer request",priority=60))
        self._validate(tasks); return tasks
    def _validate(self,tasks):
        ids={t.id for t in tasks}
        for t in tasks:
            unknown=[x for x in t.depends_on if x not in ids]
            if unknown: raise DependencyError(f"unknown dependencies: {unknown}")
        indeg={t.id:len(t.depends_on) for t in tasks}; by=defaultdict(list)
        for t in tasks:
            for d in t.depends_on: by[d].append(t.id)
        q=deque([k for k,v in indeg.items() if v==0]); seen=0
        while q:
            x=q.popleft(); seen+=1
            for n in by[x]:
                indeg[n]-=1
                if indeg[n]==0:q.append(n)
        if seen != len(tasks): raise DependencyError("dependency cycle detected")
    def ready(self,tasks):
        done={t.id for t in tasks if t.status=="done"}
        return sorted([t for t in tasks if t.status=="pending" and all(d in done for d in t.depends_on)],key=lambda t:(-t.priority,t.id))
    def layers(self,tasks):
        done=set(); rem={t.id:t for t in tasks}; layers=[]
        while rem:
            layer=sorted([t for t in rem.values() if all(d in done for d in t.depends_on)],key=lambda x:(-x.priority,x.id))
            if not layer: raise DependencyError("unresolved dependency graph")
            layers.append(layer)
            for t in layer: done.add(t.id); rem.pop(t.id)
        return layers
