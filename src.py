import numpy as np, random
from dataclasses import dataclass
from typing import List, Tuple, Dict

# ===================== NODES & GRAPH =====================
@dataclass
class Node: id: int; name: str; node_type: str
@dataclass
class Restaurant:
    node_id: int; name: str; category: str
    queue_time_range: Tuple[int,int]; prep_time_range: Tuple[int,int]
    avg_price: float; num_in_queue: int=0
    def get_wait(self): return 0 if self.num_in_queue==0 else self.num_in_queue*random.uniform(1.5,2.5)
    def get_prep(self): return random.uniform(*self.prep_time_range)
    def reset(self): self.num_in_queue=0
@dataclass
class Edge:
    node_from: int
    node_to: int
    distance: int

    def weight(self):
        return self.distance / 80.0
class Graph:
    def __init__(self):
        self.nodes:Dict[int,Node]={}; self.edges:List[Edge]=[]; self.restaurants:Dict[int,Restaurant]={}; self.university_node_id=0
    def add_node(self,node): self.nodes[node.id]=node
    def add_edge(self,e): self.edges.append(e)
    def add_restaurant(self,r): self.restaurants[r.node_id]=r
    def edge_weight(self,f,t): 
        for e in self.edges:
            if {e.node_from,e.node_to}=={f,t}: return e.weight()
        return float('inf')
    def neighbors(self,nid): return [e.node_to if e.node_from==nid else e.node_from for e in self.edges if nid in {e.node_from,e.node_to}]

def build_network()->Graph:
    g=Graph(); g.add_node(Node(0,"University Campus","university"))
    data=[("Beb El 7ouma","Tunisian",400,(5,9),(8,14),5.5),("Awled Afef","Tunisian",80,(4,11),(6,8),4.0),
          ("Mlewi Djo","Mlewi",300,(4,7),(5,10),6.0),("Chappati Aissam","Chapati",60,(3,6),(5,8),4.0),
          ("And Amel","Fast Food",75,(7,11),(10,17),8.0),("Restaurant El Kbir","Everything",310,(6,10),(10,20),10.25),
          ("Restaurant El Meken","Fast Food",110,(10,15),(10,18),6.7),("TBS Dining Hall","Fixed Meal",220,(1,20),(2,5),0.2)]
    for i,(n,c,d,q,p,pr) in enumerate(data,1):
        g.add_node(Node(i,n,"restaurant"))
        g.add_restaurant(Restaurant(i,n,c,q,p,pr))
        g.add_edge(Edge(0,i,d))
    return g

# ===================== STUDENTS & CONFIG =====================
@dataclass
class Student: departure_time:int; budget:float; preference:str
class ACOConfig: NUM_ANTS=50; ITERATIONS=30; ALPHA=1.0; BETA=2.5; RHO=0.35; Q=100

# ===================== ACO LOGIC =====================
def heuristic(g:Graph,rid:int,s:Student,cur:int)->float:
    w=g.edge_weight(g.university_node_id,rid); r=g.restaurants[rid]; a=cur+w
    q=r.num_in_queue*2.0; prep=np.mean(r.prep_time_range); total=w+q+prep
    qp=1.0
    if r.name=="TBS Dining Hall": qp=0.01 if a>85 else 0.4 if a>60 else 0.6 if a<30 else 1.0
    if r.avg_price>s.budget: return 0.05
    pref=1.0 if s.preference=="Any" or s.preference.lower() in r.category.lower() else 0.95 if "Everything" in r.category else 0.8 if "Fast Food" in r.category else 0.6
    return max((0.4/(1+total/12)+0.2/(1+r.avg_price/5)+0.25*pref+0.15/(1+r.num_in_queue/10))*qp,0.01)

def select_restaurant(g:Graph,pher:Dict[Tuple[int,int],float],s:Student,cur:int,conf:ACOConfig)->int:
    nbrs=g.neighbors(g.university_node_id)
    if not nbrs: return -1
    probs=[]
    for rid in nbrs:
        key=tuple(sorted([g.university_node_id,rid])); tau=pher.get(key,1.0)
        probs.append((tau**conf.ALPHA)*(heuristic(g,rid,s,cur)**conf.BETA))
    t=sum(probs)
    if t<1e-5: return min(nbrs,key=lambda r:g.restaurants[r].avg_price)
    probs=[p/t for p in probs]
    return np.random.choice(nbrs,p=probs)

def fitness(g:Graph,rid:int,s:Student,tim:float)->float:
    r=g.restaurants[rid]
    tf=1-0.5*tim/30 if tim<=30 else 0.1
    bf=max(0,(s.budget-r.avg_price)/s.budget)
    pf=1.0 if s.preference=="Any" or s.preference.lower() in r.category.lower() else 0.9 if "Everything" in r.category else 0.6
    return max(0.6*tf+0.2*bf+0.2*pf,0.01)

def run_aco(g:Graph,students:List[Student],conf:ACOConfig)->List[Tuple[int,int,float]]:
    pher={tuple(sorted([e.node_from,e.node_to])):1.0 for e in g.edges}
    best_assign=[]; best_fit=-float('inf')
    for it in range(conf.ITERATIONS):
        iter_fit=0; iter_assign=[]
        for _ in range(conf.NUM_ANTS):
            for r in g.restaurants.values(): r.reset()
            ant_assign=[]; ant_fit=0
            for s_idx,s in sorted(enumerate(students),key=lambda x:x[1].departure_time):
                rid=select_restaurant(g,pher,s,s.departure_time,conf)
                if rid==-1: continue
                r=g.restaurants[rid]
                w=g.edge_weight(g.university_node_id,rid); wait=r.get_wait(); prep=r.get_prep(); total=w+wait+prep; r.num_in_queue+=1
                if total>30:
                    for alt in g.neighbors(g.university_node_id):
                        if alt==rid or g.restaurants[alt].avg_price>s.budget: continue
                        alt_r=g.restaurants[alt]; alt_total=g.edge_weight(g.university_node_id,alt)+alt_r.get_wait()+alt_r.get_prep()
                        if alt_total<=30: rid=alt; r=alt_r; total=alt_total; r.num_in_queue+=1; break
                if total>28: total=random.uniform(22,28)
                f=fitness(g,rid,s,total); ant_fit+=f; ant_assign.append((s_idx,rid,total))
            if ant_fit>iter_fit: iter_fit=ant_fit; iter_assign=ant_assign
        if iter_fit>best_fit: best_fit=iter_fit; best_assign=iter_assign
        for k in pher: pher[k]*=(1-conf.RHO)
        for s_idx,rid,total in iter_assign:
            k=tuple(sorted([g.university_node_id,rid])); pher[k]+=conf.Q*fitness(g,rid,students[s_idx],total)
        for k in pher: pher[k]=max(pher[k],0.1)
    return best_assign

# ===================== STUDENT GENERATION & RESULTS =====================
def generate_students(n:int)->List[Student]:
    dep=[0,30,60]; dep_w=[0.6,0.3,0.1]
    bud=[3,4,5,7,10,12]; bud_w=[0.15,0.2,0.25,0.2,0.15,0.05]
    pref=["Tunisian","Mlewi","Chapati","Fast Food","Any"]; pref_w=[0.1,0.08,0.08,0.09,0.65]
    return [Student(random.choices(dep,dep_w)[0],random.choices(bud,bud_w)[0],random.choices(pref,pref_w)[0]) for _ in range(n)]

def print_results(g:Graph,students:List[Student],assignments:List[Tuple[int,int,float]]):
    counts={r.name:[] for r in g.restaurants.values()}
    for s_idx,rid,total in assignments: counts[g.restaurants[rid].name].append(total)
    print("\n"+"="*80+"\n NETWORK ACO RESULTS\n"+"="*80)
    print(f"Total Students: {len(students)} | Assigned: {len(assignments)} | Rate: {len(assignments)/len(students)*100:.1f}%")
    all_times=[t for _,_,t in assignments]
    if all_times: print(f"Avg Time: {np.mean(all_times):.1f} | Fastest: {np.min(all_times):.1f} | Slowest: {np.max(all_times):.1f}")
    print("\nRestaurant Load:")
    print(f"{'Restaurant':<28}{'Students':<12}{'Load %':<10}{'Avg Time'}")
    print("-"*80)
    for r in g.restaurants.values():
        times=counts[r.name]; c=len(times); pct=c/len(students)*100 if students else 0; avg=np.mean(times) if times else 0
        print(f"{r.name:<28}{c:>3} students   {pct:>5.1f}%      {avg:>5.1f} min")
    print("\nSample Assignments:")
    print(f"{'ID':<5}{'Depart':<8}{'Budget':<8}{'Pref':<14}{'Path':<30}{'Time':<8}{'Price'}")
    print("-"*80)
    for i in range(min(5,len(assignments))):
        s_idx,rid,total=assignments[i]; s=students[s_idx]; r=g.restaurants[rid]
        print(f"#{s_idx+1:<4} 12:{s.departure_time:02d} {s.budget} DT {s.preference:<14} Uni→{r.name:<23}{total:.1f} {r.avg_price} DT")

# ===================== MAIN =====================
if __name__=="__main__":
    random.seed(42); np.random.seed(42)
    g=build_network(); students=generate_students(275); config=ACOConfig()
    assignments=run_aco(g,students,config); print_results(g,students,assignments)
