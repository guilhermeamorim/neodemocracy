from threading import Thread
from threading import Event
import time
import random
import numpy
import cPickle as pickle

### PARAMETERS ####### 

NUMBER_CITIZENS = 5000
NUMBER_REPRESENTATIVES = 30
EXPECTED_NUMBER_OF_FRIENDS = 50
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
        self.budget = budget
        self.units = 0
        self.location = location
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
        self.citizens_projects = []
        self.representants_projects = []

    def select_projects(projects_list):
        """
            Computes the votes received by every project and, based on the budget, choses the ones
            that will be executed.
            Returns: list of projects that have been chosen for execution
        """
        
        return []

        
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
        # This content is dynamic and works like a queue that is analysed and discard
        self.news_feed = []
        
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
        
        # INSERT CODE
        # Evaluate 
        
        return True

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
        
    def create_project(self):
        """
            Randomly create a project that represents his/her opinion.
            
            MODEL: ?
        """
        
        project = None
        
        return project
    
    def vote_projects(self, projects_list):
        """
            Gets the list of projects and chooses which projects should by approved.
            This process is implemented by the allocation of units in the projects.
            For example: a citizen has 10 units to distribute over 100 projects. 
            He can allocate 10 on only one project or choose 10 projects and allocate 1 unit per project.
            
            Returns: list of tuples (project, units)
            units are integers numbers > 0.
        """
        
        return []
    
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
    simulate_sharing_ideas(city, 100)
    

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



def main():
    global CITY_10000
    filename = CITY_10000
    try:
        pkl_file = open(filename+'_1', 'rb')
        city = load(filename)
    except IOError:
        raw_input('File %s not found. Press any key to create a new one' % (filename,))
        city = create_game()
        dump(city, filename)    
    
    start_game(city)

def dump(city, filename):
    number_citizens = len(city.citizens)
    number_files = number_citizens / 200
    for k in range(number_files):
        i = (200*k)
        f = (200*k) + 200
        list_to_save = city.citizens[i:f].copy()
        pkl_file = open(filename+'_'+str(k), 'wb')
        pickle.dump(list_to_save, pkl_file)
        pkl_file.close()
    
def load(filename):
    print "Loading: " +  filename
    i = 0
    list_complete = []
    while True:
        try:
            pkl_file = open(filename+'_'+str(i), 'rb')
            list_citizens = pickle.load(pkl_file)
            list_complete = list_complete + list_citizens
            i+=1
            pkl_file.close()
        except IOError:
            break    
        
    city = City()
    city.citizens = list_complete
    return city
        

if __name__ == '__main__':
	main()