# ACO Lunch Optimization

This project simulates an **Ant Colony Optimization (ACO) algorithm** to assign students to lunch restaurants efficiently. The goal is to optimize **time, budget, preferences, and queue congestion** while keeping all students served within 30 minutes.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Features](#features)
* [Team Members](#team-members)
* [Installation](#installation)
* [Usage](#usage)
* [Project Structure](#project-structure)
* [Algorithm Details](#algorithm-details)
* [Configuration](#configuration)
* [Output](#output)

---

## Project Overview

The ACO Lunch Optimization project models a real-world scenario where students decide where to have lunch based on:

* Distance to the restaurant
* Current queue and waiting times
* Food preparation time
* Budget constraints
* Food preferences

It leverages **Ant Colony Optimization**, a metaheuristic inspired by real ant foraging behavior, to find near-optimal assignments.

---

## Features

* Simulates multiple students and restaurants.
* Considers walking time, queue time, and meal preparation.
* Incorporates student preferences and budget.
* Assigns students to restaurants ensuring **most under 30 minutes total time**.
* Uses **pheromone updates** to improve assignments over iterations.

---

## Team Members

This project was developed collaboratively by **5 team members**:

* Yasmine Tbessi
* Yassmine Majoul
* Oumaima Nechi
* Kenza Chanmaoui
* Wael Hajji

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yismin/aco-lunch-optimization.git
cd aco-lunch-optimization
```

2. Install dependencies:

```bash
pip install numpy
```

---

## Usage

Run the program using Python:


The script will:

1. Generate a student population (default: 275 students).
2. Load predefined restaurant data.
3. Run the ACO algorithm.
4. Print detailed results:

* Time statistics
* Restaurant distribution
* Sample student assignments

---

## Project Structure

```
aco-lunch-optimization/
├── src.py              # Main script
├── graph.py            #Graph Structure
├── README.md           # Project documentation
└── restaurants_dataset.txt    # raw data 
```

### Key Components

* **Restaurant Class**: Represents each restaurant with queue and preparation time.
* **Student Class**: Represents students with departure time, budget, and preference.
* **ACO Algorithm**: Assigns students iteratively, updating pheromones to optimize selection.
* **Heuristic Function**: Scores restaurants based on total time, price, congestion, and preference.
* **Fitness Evaluation**: Measures assignment quality for each student-restaurant pair.
* **Result Printing**: Summarizes assignments, restaurant load, and time statistics.

---

## Algorithm Details

1. **Initialization**:

   * Set initial pheromones.
   * Reset restaurant queues.

2. **Ant Iterations**:

   * Each ant simulates student assignments.
   * Students choose restaurants probabilistically using **pheromones** and **heuristics**.

3. **Heuristic Calculation**:

   * Combines walking time, queue, prep time, price, congestion, and preference.
   * Special handling for TBS Dining Hall based on arrival time.

4. **Fitness Evaluation**:

   * Rewards fast assignments (<30 min), budget efficiency, and preference satisfaction.

5. **Pheromone Update**:

   * Increases pheromones on good paths, decreases globally for evaporation.

6. **Iteration**:

   * Repeat for the configured number of iterations to improve assignments.

---

## Configuration

Adjust ACO parameters via the `ACOConfig` class:

```python
class ACOConfig:
    NUM_ANTS = 50        # Number of ants per iteration
    ITERATIONS = 30      # Total iterations
    ALPHA = 1.0          # Influence of pheromone
    BETA = 2.5           # Influence of heuristic
    RHO = 0.35           # Pheromone evaporation rate
    Q = 100              # Pheromone deposit factor
```

Other configurable options:

* Number of students in `generate_students(n)`
* Restaurant data in `load_restaurants()`

---

## Output

### Summary

```
Total Students: 275
Assigned: 275
Assignment Rate: 100.0%
Average Time: 23.5 min
Fastest Service: 6.4 min
Slowest Service: 27.9 min
```

### Restaurant Distribution

| Name                | Students | Load % | Avg Time |
| ------------------- | -------- | ------ | -------- |
| Beb El 7ouma        | 15       | 5.5    | 23.6     |
| Awled Afef          | 36       | 13.1   | 22.4     |
| Mlewi Djo           | 16       | 5.8    | 21.9     |
| Chappati Aissam     | 43       | 15.6   | 23.0     |
| And Amel            | 11       | 4.0    | 22.1     |
| Restaurant El Kbir  | 6        | 2.2    | 24.1     |
| Restaurant El Meken | 14       | 5.1    | 22.4     |
| TBS Dining Hall     | 134      | 48.7   | 24.3     |

### Sample Student Assignments

```
ID   Depart  Budget  Pref          Restaurant               Time    Price
#2   12:00   7 DT    Any           Restaurant El Meken      15.7    6.7 DT
#4   12:00   4 DT    Any           Awled Afef               8.2    4.0 DT
#5   12:00   4 DT    Any           Chappati Aissam          6.4    4.0 DT
#6   12:00   4 DT    Any           TBS Dining Hall          6.5    0.2 DT
#10  12:00   10 DT   Any           TBS Dining Hall          7.9    0.2 DT
```

---

