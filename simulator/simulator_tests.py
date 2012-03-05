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
    city = simulator.load_game('network1.sim')

    city.create_random_proposals()
    #simulate_sharing_ideas(city, 5)
    city.like_projects(1)
    city.select_proposals()
    city.vote_projects()
#    city.vote_projects_representatives()
#    city.select_approved_projects()

    return city

def test_happiness_level(city):
    for citizen in city.citizens:
        print str(citizen.compute_happiness_level(city.projects_approved)) + " "

def test_representative(city):
    c = city.citizens[0]
    rep = simulator.Representative(c.id, c.location, c.influence_level, c.proactivity_level)
    print "ID: "+str(rep.id)
    print "LOC: "+str(rep.location)
    print type(rep)
    rep.vote_projects_representative(city.projects_for_vote)
    

#def main():
    #test_recalculate_opinions()
    #city = test_projects()
    #test_happiness_level(city)
city = test_projects()
#test_representative(city)
c = city.citizens[0]
rep = simulator.Representative(c.id, c.location, c.influence_level, c.proactivity_level, c.opinions)
print "ID: "+str(rep.id)
print "LOC: "+str(rep.location)
print type(rep)
#rep.vote_projects_representative(city.projects_for_vote)

    
"""    
if __name__ == '__main__':
    main()
"""
