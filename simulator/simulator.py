from threading import Thread
from threading import Event
import time
import random
import numpy
import cPickle as pickle

### PARAMETERS ####### 

NUMBER_CITIZENS = 500
NUMBER_REPRESENTATIVES = 30
EXPECTED_NUMBER_OF_FRIENDS = 50
UNITS_PER_CITIZEN = 10
ANNUAL_BUDGET = 10000000 # 10 millions
MAX_NUMBER_PROPOSALS = 500
MAX_NUMBER_PROJECTS = 50

#lambda_exponential = 1/(NUMBER_CITIZENS/10.)
#lambda_exponential = 1/(2000/10.)

# the categories in which an idea might be related to.
# we assume that an idea is related to only one category
CATEGORIES = [1,2,3,4,5,6,7]
INFLUENCE_LEVELS = [1,2]
LOCATIONS = [1,2,3,4,5,6,7,8,9,10]
PROACTIVITY_LEVELS = ['F', 'D', 'C']

CITY_10000 = 'city10000/city10000'

#######################




class Idea:
    def __init__(self, id, description, category, weight):
        self.id = id #integer
        self.description = description #string
        self.category = category #[1,7] integers
        self.weight = weight #[-1, 1] float

class Project:
    def __init__(self, id, description, category, budget, location):
        self.id = id #integer
        self.description = description #string
        self.category = category #[1,7] integers
        self.location = location
        self.budget = budget
#        self.units = numpy.random.random_integers(1,1000)
#        self.likes = numpy.random.random_integers(1,1000)
        self.units = 0
        self.likes = 0
        self.dontlikes = 0

class City:
    """
        Encapsulates the backlog of the projects of the city and its budget.
        Includes projects for all subjects and locations.
        Since this simulations is initially focused on one city, there will be only one 
        instance of this class during the simulation.
    """
    def __init__(self):
        self.citizens = []
        self.annual_budget = 0
        self.proposals = []
        self.projects_for_vote = []
        self.projects_approved = []

    def create_random_proposals(self):
        """
            Simulates the creation of a set of proposals (citizen projects)
        """ 
        global MAX_NUMBER_PROPOSALS
        global LOCATIONS
        global CATEGORIES
        
        for i in range(MAX_NUMBER_PROPOSALS):
            description = ""
            location = random.choice(LOCATIONS)
            category = random.choice(CATEGORIES)
            budget = random.uniform(500000, 1000000)
            project = Project(i, description, category, budget, location)
            self.proposals.append(project)

    def select_proposals(self):
        """
            Select proposals that will be chosen for voting.
        """
        print "Selecting proposals... "
        global MAX_NUMBER_PROJECTS
        proposals_sorted = sorted(self.proposals, key=lambda project:project.likes, reverse=True)
        for i in range(MAX_NUMBER_PROJECTS):
            self.projects_for_vote.append(proposals_sorted[i])

    def select_approved_projects(self):
        """
            Computes the votes received by every project and, based on the budget, choses the ones
            that will be executed.

            Returns: list of projects that have been approved for execution
        """
        print "Selecting approved projects... "
        global ANNUAL_BUDGET
        
        projects_sorted = sorted(self.projects_for_vote, key=lambda project:project.units, reverse=True)
        budget_sum = 0
        for p in projects_sorted:
            budget_sum += p.budget
            if budget_sum <= ANNUAL_BUDGET:
                self.projects_approved.append(p)


    def like_projects(self, t):
        """
            Repeates t times.
        """
        print "Liking projects... %d times" % (t,)
        # 20% is "liking"
        random_likers = random.sample(self.citizens, int(len(self.citizens)*0.2))
        for citizen in random_likers:
            for project in self.proposals:
                like = citizen.like(project)
                if like:
                    project.likes += 1
                    

    def vote_projects(self):
        """
        
        """
        print "Voting projects... "
        # 60% is voting
        random_voters = random.sample(self.citizens, int(len(self.citizens)*0.6))
        for citizen in random_voters:
            dic_projects_units = citizen.vote_projects(self.projects_for_vote)
            for element in dic_projects_units:
                project_id = element
                project_units = dic_projects_units[element]
                project = None
                
                # needs to enhance performance. Think about it.
                for p in self.projects_for_vote:
                    if p.id == project_id:
                        project = p
                        break
                if project:
                    project.units += project_units



class Calendar:
    """
        This class 
    """
    def __init__(self):
        self.years = []
        self.indicators = []

    def add_project(self, project):
        self.projects.append(project)
        
    
        
class Citizen():
    """
        Citizen class
        Represents a citizen in the model.
        Every citizen is node in the graph and is linked to a set of friends, having influence over them and 
        being influenced by them.
        
    """
    def __init__(self,id):
        
        self.id=id
        self.location1 = None
        
        # INFLUENCE LEVEL
        # let's start with a discrete model (3 levels) 1, 2 or 3.
        # level 1 means that the ideas spread reaches only friends (1 level on the graph)
        # level 2 means that the ideas spread reaches only friends of friends (2 levels on the graph)
        # level 3 means that the ideas spread reaches only friends of friends of friends (3 levels on the graph)
        self.influence_level = None
        
        # PROACTIVITY LEVEL
        # creators / distributors / followers
        # notice that there is an inheritance relation between them.
        # every creator is a distributor and a follower
        # every disitributor is a follower.
        # creator: creates projects
        # distribuitor: share ideas
        # follower: is influence by the ideas received.
        self.proactivity_level = None
        
        self.friends = []
        
        # OPINIONS
        # list of IDEAS that represents the citizen's belief regarding several subjects.
        # Theses subjects are represented in this simulator by categories.
        self.opinions = {}
        
        # Don't remember why this attribute was included.
        self.projects = []
        
        # Ideas received to be processed. 
        # incluences the opinion.
        # This content is dynamic and works like a queue that is analysed and discarded
        self.news_feed = []
        
        # used for search algorithms.
        # has no meaning in the model.
        self.color = 'W'
    
    
    def _get_friends_random_list(self, citizen):
        """
            Returns a list o random friends of the citizen passed as argument.
            For the moment we've chosen 5 to 20% of friends.
        """
        
        number_friends = int(random.uniform(len(citizen.friends)*0.05, len(citizen.friends)*0.2))
        return random.sample(citizen.friends, number_friends)
    
    def share_ideas(self):
        """
            This method implements the process of sharing ideas with friends in the network.
            It's implemented by submiting/sending/posting some ideas to a random number of friends.
            This submisson is made by adding ideas objects into the attribute news_feed of the choosen friends.
            The news_feed attribute works like a FIFO queue.
            Defining the number of friends to which the ideas are sent is a function that involves 2 variables:
            1. a normal random variable (Mean: number of friends / 3, Std. Dev: ??)
            2. influence_level of the citizen.
            number_friends_to_share = random_number * influence_factor
            
            After defining a number of friends to share, this method randomly selects the friends in its friend list.
        """
        global CATEGORIES
        
        # F citizens (followers) do not share        
        if self.proactivity_level != 'F':
            random_list_friends = self._get_friends_random_list(self)
            if self.influence_level >= 1:
                for friend in random_list_friends:
                    idea = self.opinions[random.choice(CATEGORIES)]
                    friend.news_feed.append(idea)
                    
                    if self.influence_level >= 2:
                        random_list_friends2 = self._get_friends_random_list(friend)
                        for friend2 in random_list_friends2:
                            friend2.news_feed.append(idea)

                            if self.influence_level >= 3:
                                random_list_friends3 = self._get_friends_random_list(friend2)
                                for friend3 in random_list_friends3:
                                    friend3.news_feed.append(idea)
                        

    def like(self, project):
        """
            Return True, if the citizen agrees with the project, or False, if he doesn't.
            Evaluate the opinion and the characteristics of the project and, based on a probabilistic model, 
            returns True or False.
            MODEL: ?
            
        """
        like = False
        cat = project.category
        idea = self.opinions[cat]
        if idea.weight > 0.5:
            like = True
        
        return like

    def _recalculate_opinions(self, idea):
        """
            Every idea a citizen is submitted to influences his opinion.
            This is implemented by adjusting the opinion attribute of the citizen.
            MODEL: ?
        """
        
        last_idea = self.opinions[idea.category]
        last_idea.weight = last_idea.weight+(idea.weight*0.05)
        if last_idea.weight >1:
            last_idea.weight = 1
        elif last_idea.weight <-1:
            last_idea.weight = -1
    
    def recalculate_opinions(self):
        """
            Recalcultes the opinions based on the self.news_feed attribute
        """
        for i in range(len(self.news_feed)):
            idea = self.news_feed.pop()
            self._recalculate_opinions(idea)
        
    
    def vote_projects(self, projects_list):
        """
            Gets the list of projects and chooses which projects should by approved.
            This process is implemented by the allocation of units in the projects.
            For example: a citizen has 10 units to distribute over 100 projects. 
            He can allocate 10 on only one project or choose 10 projects and allocate 1 unit per project.
            
            Returns: a dictionary (project_id, units)
            units are integers numbers > 0.
        """
        global UNITS_PER_CITIZEN
        dic_return = {}
        
        decorated = [(project.likes*self.opinions[project.category].weight, project) for project in projects_list]
        decorated.sort()
        
        dic_return[decorated[0][1].id] = int(UNITS_PER_CITIZEN/2)
        dic_return[decorated[1][1].id] = int(UNITS_PER_CITIZEN/3)
        dic_return[decorated[2][1].id] = int(UNITS_PER_CITIZEN/6)
        
        return dic_return
    
    def vote_representatives(self, representatives_list):
        """
            Chooses the representative
        """
        representative = 0
        
        return representative
        
    def recompute_friends(self):
        """
            Based on the degree of similarity of opinion, this function computes the
            new network of friends for a citizen.
            Gives the network a more organic life. Takes into account the influences of ideas in the 
            stablishment of new connections and the deletion of connections.
        """
    
        return True


class Representative(Citizen):
    """
        Implements the representatives of the citizens.
        Every representative is also a citizen.
        
        The process of chosing the proposals and the projects is similar to the citizen's.
        In the case of proposals, 
    """
    def __init__(self, id, location, influence_level, proactivity_level):
        super(Citizen, self).__init__(id, location, influence_level, proactivity_level)
        
    def select_proposals(proposals_list):
        """
            Choose, based on their opinions and on the likes received, proposals which will become projects.
            
            Returns: list of (projects, units)
        """
        
        return []
        

#####################################
##### GAME SIMULATION BEGINS HERE  ##
#####################################

def start_game(city):
    simulate_sharing_ideas(city, 10)
    city.create_random_proposals()
    simulate_sharing_ideas(city, 10)
    city.like_projects(50)
    city.select_proposals()
    city.vote_projects()
    city.select_approved_projects()
#    save_statistics()
    
    

def simulate_sharing_ideas(city, k):
    """
        Runs the sharing ideas procedure k times
        and then recalculates the opinions
    """
    print "Simulating ideas sharing... " + str(k) + " runs"
    for r in range(k):
        for citizen in city.citizens:
#            print "Citizen %d - Friends: %d - Opinions: %d - IL: %d" % (citizen.id, len(citizen.friends), len(citizen.opinions),\
#                citizen.influence_level)
            citizen.share_ideas()
#        for citizen in city.citizens:
#            print "Citizen %d - NewsFedd: %d" % (citizen.id, len(citizen.news_feed))

    print "Recalculating opinions... "
    for citizen in city.citizens:
        citizen.recalculate_opinions()
    

#####################################
##### GAME SIMULATION ENDS HERE  ####
#####################################




#####################################
##### GAME CREATION BEGINS HERE  ####
#####################################

def create_game():
    city = City()
    global NUMBER_CITIZENS
    global EXPECTED_NUMBER_OF_FRIENDS
    create_graph(city, NUMBER_CITIZENS, EXPECTED_NUMBER_OF_FRIENDS)
    first_representatives(city, NUMBER_REPRESENTATIVES)
    return city

def first_representatives(city, number_representatives):
    representatives = random.sample(city.citizens, number_representatives)
    city.representatives = representatives
    for rep in representatives:
        rep.influence_level = 2
        rep.proactivity_level = 'C'

def setup_random_friends(city, number_citizens, expected_number_of_friends):
    for citizen in city.citizens:
        number_friends = int(random.uniform(0,expected_number_of_friends*2))
        print "Citizen %d - Friends: %d - Opinions: %d" % (citizen.id, number_friends, len(citizen.opinions))
        
        for i in range(number_friends):
            friend = random.choice(city.citizens)
            if friend != citizen and friend not in citizen.friends:
                citizen.friends.append(friend)
                friend.friends.append(citizen)


def setup_random_opinions():
    """
        Return a set of ideas.
        We assume that every citizen will have opinions about every category.
    """
    global CATEGORIES
    
    ideas_dic = {}
    
    for i in CATEGORIES:
        idea = Idea(1,"",i, random.uniform(-1,1))
        ideas_dic[i] = idea
        
    return ideas_dic

def setup_random_influence_level():
    """
        10% - level 2
        90% - level 1
    """
    
    global INFLUENCE_LEVELS
    number = random.uniform(0,1)
    index = 0
    if number<=0.9:
        index = 0
    else:
        index = 1
    return INFLUENCE_LEVELS[index]

def setup_random_proactivity_level():
    """
        5% creators
        10% distributors
        85% followers
    """

    global PROACTIVITY_LEVELS
    number = random.uniform(0,1)
    index = 0
    if number<=0.05:
        index = 2
    elif 0.05 < number <= 0.15:
        index = 1
    else:
        index = 0
    return PROACTIVITY_LEVELS[index]

def setup_random_location():
    """
    """

    global LOCATIONS
    location = random.choice(LOCATIONS)
    return location


def create_random_citizen(i):
    citizen = Citizen(i)
    citizen.opinions = setup_random_opinions()
    citizen.influence_level = setup_random_influence_level()
    citizen.location = setup_random_location()
    citizen.proactivity_level = setup_random_proactivity_level()
    return citizen
    
        
def create_graph(city, number_citizens, expected_number_of_friends):
    
    for i in range(number_citizens):
        citizen = create_random_citizen(i)
        city.citizens.append(citizen)
        
    setup_random_friends(city, number_citizens, expected_number_of_friends)
    

def check_graph():
    global citizens_list
    for citizen in citizens_list:
        print "Citizen: " +  str(citizen.id) + "\n"
        for friend in citizen.friends:
            print friend.id,
        print "\n"

def dfs_visit(citizen):
    citizen.color = 'G'
    for friend in citizen.friends:
        if friend.color == 'W':
            dfs_visit(friend)
    citizen.color = 'B'
    print citizen.id
        
def depth_firts_search():
    global citizens_list
    for citizen in citizens_list:
        citizen.color = 'W'
    
    for citizen in citizens_list:
        if citizen.color == 'W':
            dfs_visit(citizen)


#####################################
##### GAME CREATION ENDS HERE  ####
#####################################



##############################################
##### SAVING DATA INTO FILES - START #########
##############################################


def save_graph(graph):
    """
        The graph passed as argument to this function is a list of citizens
    """
    file_name = 'network1.sim'
    print "Saving network into "+file_name
    f = open(file_name, 'w')
    f.write(str(len(graph))+'\n')
    for citizen in graph:
        f.write(str(citizen.id) + ';' + str(citizen.location) + ';' + str(citizen.influence_level) + ';' + \
            str(citizen.proactivity_level) + '\n')
        for op in citizen.opinions.keys():
            value = citizen.opinions[op].weight
            f.write(str(op)+':'+str(value)+';')
        f.write('\n')
        for friend in citizen.friends:
            f.write(str(friend.id) + ';')
        f.write('\n')
    f.close()


def load_graph(file_name):
    """
        Loads the graph saved on the file.
        returns a list of citizens with its attributes set.
    """
    citizens = []
    f = open(file_name, 'r')
    number_citizens = int(f.readline())
    
    # creates the citizen's list.
    for i in range(number_citizens):
        # creates citizen object
        citizen = Citizen(i)
        citizens.append(citizen)

    # we need this second loop because we cannot create the list of friends 
    # if we don't have the whole list of citizens in memory.
    for citizen in citizens:
        # loads basic infor
        inf_list = f.readline().split(';')
        citizen.location = int(inf_list[1])
        citizen.influence_level = int(inf_list[2])
        citizen.proactivity_level = inf_list[3]
        
        # loads opinions
        opinions_list = f.readline().split(';')
        opinions = {}
        
        for op in opinions_list[:-1]:
            cat_weight = op.split(':')
            print cat_weight
            cat = int(cat_weight[0])
            weight = float(cat_weight[1])
            idea = Idea(1,'',cat, weight)
            opinions[cat] = idea

        citizen.opinions = opinions
              
        # loads friends      
        friends_ids_list = f.readline().split(';')
        friends = []
        for friend_id in friends_ids_list[:-1]:
            # note that we match the position of the citizen in the citizens list with its id.
            friends.append(citizens[int(friend_id)])
        
        citizen.friends = friends
        
    f.close()
    
    return citizens
    


##############################################
##### SAVING DATA INTO FILES - END ###########
##############################################








def main():
    city = create_game()
    save_graph(city.citizens)
    load_graph('network1.sim')
    #start_game(city)
"""
if __name__ == '__main__':
	main()
"""
