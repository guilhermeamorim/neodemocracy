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

def test_projects():
    city = simulator.create_game()
    simulator.start_game(city)
    print "Proposals: %d | Projects for vote: %d | Projects approved: %d" % (len(city.proposals), len(city.projects_for_vote), \
        len(city.projects_approved))
    print "Creating proposals"
    city.create_random_proposals()
    print "Proposals: %d | Projects for vote: %d | Projects approved: %d" % (len(city.proposals), len(city.projects_for_vote), \
        len(city.projects_approved))

    print "Selecting proposals"
    city.select_proposals()
    print "Proposals: %d | Projects for vote: %d | Projects approved: %d" % (len(city.proposals), len(city.projects_for_vote), \
        len(city.projects_approved))

    print "Approved projects"
    city.select_approved_projects()
    print "Proposals: %d | Projects for vote: %d | Projects approved: %d" % (len(city.proposals), len(city.projects_for_vote), \
        len(city.projects_approved))


def main():
    #test_recalculate_opinions()
    test_projects()
    
if __name__ == '__main__':
    main()
