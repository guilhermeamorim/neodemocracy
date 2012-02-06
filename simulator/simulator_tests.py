"""
    Simulator testing
"""

import unittest
import simulator
import random

def test_recalculate_opinions():
    citizen = simulator.create_random_citizen(10)
    idea = simulator.Idea(1,"",random.choice([1,2,3,4,5,6,7]), random.uniform(-1,1))
    print citizen.opinions[idea.category].weight
    print idea.category
    print idea.weight
    citizen._recalculate_opinions(idea)
    print citizen.opinions[idea.category].weight

def main():
    test_recalculate_opinions()

if __name__ == '__main__':
    main()
