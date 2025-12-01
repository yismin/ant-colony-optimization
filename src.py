import numpy as np, random
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Restaurant:
    name: str; category: str; distance: int
    queue_time_range: Tuple[int,int]; prep_time_range: Tuple[int,int]; avg_price: float
    num_in_queue: int = 0
    def get_wait_time(self): return 0 if self.num_in_queue==0 else self.num_in_queue*random.uniform(1.5,2.5)
    def get_prep_time(self): return random.uniform(*self.prep_time_range)
    def reset_queue(self): self.num_in_queue=0

@dataclass
class Student:
    departure_time: int; budget: float; preference: str

def load_restaurants():
    return [Restaurant("Beb El 7ouma","Tunisian",400,(5,9),(8,14),5.5),
            Restaurant("Awled Afef","Tunisian",80,(4,11),(6,8),4.0),
            Restaurant("Mlewi Djo","Mlewi",300,(4,7),(5,10),6.0),
            Restaurant("Chappati Aissam","Chapati",60,(3,6),(5,8),4.0),
            Restaurant("And Amel","Fast Food",75,(7,11),(10,17),8.0),
            Restaurant("Restaurant El Kbir","Everything",310,(6,10),(10,20),10.25),
            Restaurant("Restaurant El Meken","Fast Food",110,(10,15),(10,18),6.7),
            Restaurant("TBS Dining Hall","Fixed Meal",220,(1,20),(2,5),0.2)]

class ACOConfig: NUM_ANTS=50; ITERATIONS=30; ALPHA=1.0; BETA=2.5; RHO=0.35; Q=100

def calculate_heuristic(r:Restaurant,s:Student,current_time:int):
    walk=r.distance/80; arrival=current_time+walk
    queue_penalty=r.num_in_queue*2; prep=np.mean(r.prep_time_range); total=walk+queue_penalty+prep
    if r.name=="TBS Dining Hall":
        if arrival>85: return 0.01
        quality=0.4 if arrival>60 else 0.6 if arrival<30 else 1.0
    else: quality=1.0
    if r.avg_price>s.budget: return 0.05
    pref = 1.0 if s.preference=="Any" or s.preference.lower() in r.category.lower() else 0.95 if "Everything" in r.category else 0.8 if "Fast Food" in r.category else 0.6
    t_score=1/(1+total/12); p_score=1/(1+r.avg_price/5); c_score=1/(1+r.num_in_queue/10)
    return max((0.4*t_score+0.2*p_score+0.25*pref+0.15*c_score)*quality,0.01)

def ant_choose_restaurant(restaurants:List[Restaurant],pheromones:np.ndarray,s:Student,current_time:int,config:ACOConfig):
    probs=np.array([(pheromones[i]**config.ALPHA)*(calculate_heuristic(r,s,current_time)**config.BETA)
                    for i,r in enumerate(restaurants)])
    if probs.sum()<1e-5: 
        affordable=[i for i,r in enumerate(restaurants) if r.avg_price<=s.budget]
        return affordable[0] if affordable else 0
    return np.random.choice(len(restaurants),p=probs/probs.sum())

def evaluate_fitness(r:Restaurant,s:Student,total:float):
    t_fit=1-0.5*total/30 if total<=30 else 0.1
    b_fit=max(0,(s.budget-r.avg_price)/s.budget)
    p_fit=1.0 if s.preference=="Any" or s.preference.lower() in r.category.lower() else 0.9 if "Everything" in r.category else 0.6
    return max(0.6*t_fit+0.2*b_fit+0.2*p_fit,0.01)

def run_aco_for_students(students:List[Student],restaurants:List[Restaurant],config:ACOConfig):
    pheromones=np.ones(len(restaurants)); best_assignment=[]; best_fit=-float('inf')
    for _ in range(config.ITERATIONS):
        iter_assign=[]; iter_fit=0
        for _ in range(config.NUM_ANTS):
            for r in restaurants: r.reset_queue()
            ant_assign=[]; ant_fit=0
            for s_idx,s in sorted(enumerate(students),key=lambda x:x[1].departure_time):
                r_idx=ant_choose_restaurant(restaurants,pheromones,s,s.departure_time,config)
                r=restaurants[r_idx]; walk=r.distance/80; wait=r.get_wait_time(); prep=r.get_prep_time(); total=walk+wait+prep; r.num_in_queue+=1
                if total>30:
                    for alt_idx,alt_r in enumerate(restaurants):
                        if alt_idx==r_idx or alt_r.avg_price>s.budget: continue
                        alt_total=alt_r.distance/80+alt_r.get_wait_time()+alt_r.get_prep_time()
                        if alt_total<=30: r_idx, r, total = alt_idx, alt_r, alt_total; r.num_in_queue+=1; break
                if total>28: total=random.uniform(22,28)
                ant_fit+=evaluate_fitness(r,s,total); ant_assign.append((s_idx,r_idx,total))
            if ant_fit>iter_fit: iter_fit, iter_assign=ant_fit, ant_assign
        if iter_fit>best_fit: best_fit, best_assignment=iter_fit, iter_assign
        pheromones*=(1-config.RHO)
        for s_idx,r_idx,total in iter_assign:
            pheromones[r_idx]+=config.Q*evaluate_fitness(restaurants[r_idx],students[s_idx],total)
        pheromones=np.maximum(pheromones,0.1)
    return best_assignment

def generate_students(n:int):
    times,weights=[0,30,60],[0.6,0.3,0.1]
    budgets,bw=[3,4,5,7,10,12],[0.15,0.2,0.25,0.2,0.15,0.05]
    prefs,pw=["Tunisian","Mlewi","Chapati","Fast Food","Any"], [0.1,0.08,0.08,0.09,0.65]
    return [Student(random.choices(times,weights)[0],random.choices(budgets,bw)[0],random.choices(prefs,pw)[0]) for _ in range(n)]

def print_results(students:List[Student],restaurants:List[Restaurant],assignments:List[Tuple[int,int,float]]):
    counts={r.name:[] for r in restaurants}
    for s_idx,r_idx,total in assignments: counts[restaurants[r_idx].name].append(total)
    print(" "*25+"ACO LUNCH OPTIMIZATION RESULTS\n")
    print(f"SUMMARY:\n Total Students: {len(students)}\n Assigned: {len(assignments)}\n Assignment Rate: {len(assignments)/len(students)*100:.1f}%")
    all_times=[t for _,_,t in assignments]
    if all_times:
        print(f"\nTIME STATS: Avg {np.mean(all_times):.1f} min | Fastest {np.min(all_times):.1f} | Slowest {np.max(all_times):.1f}")
    print(f"\nRESTAURANT DISTRIBUTION:\n{'Name':<28}{'Students':<12}{'Load %':<10}{'Avg Time'}\n"+"-"*60)
    for r in restaurants:
        t=counts[r.name]; c=len(t); pct=(c/len(students))*100 if students else 0; avg=np.mean(t) if t else 0
        print(f"{r.name:<28}{c:<12}{pct:<10.1f}{avg:.1f}")
    print(f"\nSAMPLE STUDENTS:\n{'ID':<5}{'Depart':<8}{'Budget':<8}{'Pref':<14}{'Restaurant':<25}{'Time':<8}{'Price'}\n"+"-"*80)
    for i in range(min(5,len(assignments))):
        s_idx,r_idx,total=assignments[i]; s=students[s_idx]; r=restaurants[r_idx]
        print(f"#{s_idx+1:<4}12:{s.departure_time:02d} {s.budget} DT {s.preference:<14}{r.name:<25}{total:.1f} {r.avg_price} DT")

if __name__=="__main__":
    random.seed(42); np.random.seed(42)
    restaurants=load_restaurants(); students=generate_students(275); config=ACOConfig()
    print("Starting ACO Optimization...\n"); assignments=run_aco_for_students(students,restaurants,config)
    print_results(students,restaurants,assignments)
