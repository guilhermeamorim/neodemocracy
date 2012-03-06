import random
import numpy
from scipy import stats
import math
from scipy.stats import rv_discrete

### PARAMETERS ####### 

NUMBER_CITIZENS = 10000
NUMBER_REPRESENTATIVES = 30
EXPECTED_NUMBER_OF_FRIENDS = 50
UNITS_PER_CITIZEN = 10
ANNUAL_BUDGET = 10000000 # 10 millions
MAX_NUMBER_PROPOSALS = 500
MAX_NUMBER_PROJECTS = 50

# Percentage of citizens that vote
PERCENTAGE_VOTERS = 0.1

#lambda_exponential = 1/(NUMBER_CITIZENS/10.)
#lambda_exponential = 1/(2000/10.)

# the categories in which an idea might be related to.
# we assume that an idea is related to only one category
CATEGORIES = [1,2,3]
INFLUENCE_LEVELS = [1,2]
LOCATIONS = [1,2,3,4]

# indicates the percentage of voters per location
LOCATIONS_PERC = [0.1,0.4,0.7,0.8]

# Follower, Distributor, Creator
PROACTIVITY_LEVELS = ['F', 'D', 'C']

#######################



## LOCATIONS DENSITY FUNCTION
pk = [0.25, 0.25, 0.25, 0.25]
locations_rv = rv_discrete(name='loaded', values=(LOCATIONS,pk))


## CATEGORIES DENSITY FUNCTION 
pk = [0.333, 0.333, 0.333]
categories_rv = rv_discrete(name='loaded', values=(CATEGORIES,pk))



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
        
        # political units
        self.p_units = 0
        self.likes = 0
        self.dontlikes = 0

    def __str__(self):
        return 'Project %d - Category: %d - Location: %d - Budget: %d - Units: %d - P_Units: %d - Likes: %d' % \
            (self.id, self.category, self.location, self.budget, self.units, self.p_units ,self.likes)

class City:
    """
        Encapsulates the backlog of the projects of the city and its budget.
        Includes projects for all subjects and locations.
        Since this simulations is initially focused on one city, there will be only one 
        instance of this class during the simulation.
    """
    def __init__(self):
        self.citizens = []
        self.representatives = []
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
            location = locations_rv.rvs(size=1)[0]
            category = categories_rv.rvs(size=1)[0]
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

#        raw_input("Pausa - antes")
#        for p in proposals_sorted:
#            print p
#        raw_input("Pausa - depois")
        
        

    def select_approved_projects(self):
        """
            Computes the votes received by every project and, based on the budget, choses the ones
            that will be executed.

            Returns: list of projects that have been approved for execution
        """
        print "Selecting approved projects... "
        global ANNUAL_BUDGET
        
        projects_citizens_sorted = sorted(self.projects_for_vote, key=lambda project:project.units, reverse=True)
        projects_reps_sorted = sorted(self.projects_for_vote, key=lambda project:project.p_units, reverse=True)
        budget_sum = 0
        
        for p in projects_citizens_sorted:
            budget_sum += p.budget
            if budget_sum <= ANNUAL_BUDGET/2:
                self.projects_approved.append(p)

        budget_sum = 0
        for p in projects_reps_sorted:
            if p not in self.projects_approved:
                budget_sum += p.budget
                if budget_sum <= ANNUAL_BUDGET/2:
                    self.projects_approved.append(p)


        
#        raw_input("select_approved_projects - antes")
        for p in projects_citizens_sorted:
            print p
        print "\nReps\n"
        for p in projects_reps_sorted:
            print p
        print "\nApproved\n"
        for p in self.projects_approved:
            print p

        raw_input("select_approved_projects - depois")

    def like_projects(self, t):
        """
            Repeates t times.
        """
        print "Liking projects... %d times" % (t,)
        
        for i in range(t):
            # 20% is "liking"
            random_likers = random.sample(self.citizens, int(len(self.citizens)*0.4))
            for citizen in random_likers:
                for project in self.proposals:
                    like = citizen.like(project)
                    if like:
                        project.likes += 1
                    


    def vote_projects(self):
        """
        
        """
        global PERCENTAGE_VOTERS
        random_voters = random.sample(self.citizens, int(len(self.citizens)*PERCENTAGE_VOTERS))
        print "Voting projects. %d voters." % (len(random_voters),)

        for citizen in random_voters:
            dic_projects_units = citizen.vote_projects(self.projects_for_vote)
            for project in dic_projects_units:
                project_units = dic_projects_units[project]
                project.units += project_units


    def vote_projects_representatives(self):
        """
        
        """

        print "Representatives voting.."
        for rep in self.representatives:
            #print type(rep)
            dic_projects_units = rep.vote_projects_representative(self.projects_for_vote)
            #print dic_projects_units
            #print dic_projects_units.keys()
            for project in dic_projects_units.keys():
                project_units = dic_projects_units[project]
                project.p_units += project_units


    def compute_social_happiness(self):
        """
            Returns the mean of the citizens happiness levels
        """
        citizens_happiness = []
        for citizen in self.citizens:
            citizens_happiness.append(citizen.compute_happiness_level(self.projects_approved))
        
        return stats.describe(citizens_happiness)[2]
        

    def compute_social_engagement(self):
        """
            
        """
        
        return 0


    def compute_statistics(self):
        """
            Compute statistics of a annual round of sharing ideias, liking, voting...
            Statistics:
            - Total number of ideas shared
            - Total number of likes
            - Total number of don't likes
            - Total number of votes
            - Total number of projects approved
            - Level of social engagement
            - Level of social happiness
            
            Returns a tuple with the statistics above.
            
        """

    def reset(self):
        """
            Resets values....
            
        """
        self.proposals = []
        self.projects_for_vote = []
        self.projects_approved = []

    def compute_overall_opinions(self):
        """
            Computes the histograms of the opinions for each category
        """
        opinions_list = []
        global CATEGORIES
        i=0
        for cat in CATEGORIES:
            opinions_list.append([])
            for citizen in self.citizens:
                opinions_list[i].append(citizen.opinions[cat].weight)
            i+=1
        
        i=0;
        for cat in CATEGORIES:
            mean = stats.describe(opinions_list[i])[2]
            std = math.sqrt(stats.describe(opinions_list[i])[3])
            print "Category: %d - Mean: %f - STD: %f" % (cat, mean, std)
            i+=1
        

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
        
        # Happiness level of the citizen
        # We initially consider the happiness level as a discrete dichotomous variable
        # 0 -> not happy
        # 1 -> happy
        self.happiness_level = 0
        
        
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
        rv = random.uniform(0,1)
        cat = project.category
        idea = self.opinions[cat]
        if idea.weight > -0.6 and project.location == self.location and rv > 0.6:
            like = True
        elif idea.weight > -0.3 and rv > 0.90:
            like = True
        
        return like

    def _recalculate_opinions(self, idea):
        """
            Every idea a citizen is submitted to influences his opinion.
            This is implemented by adjusting the opinion attribute of the citizen.
            MODEL: ?
        """
        
        last_idea = self.opinions[idea.category]
        last_idea.weight = last_idea.weight+(idea.weight*0.001)
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
        global LOCATIONS_PERC
        dic_return = {}
        
#        for p in projects_list:
#            print p
        
        projects_list = random.sample(projects_list, int(len(projects_list)*0.4))
        rv = random.uniform(0,1)
        
        if rv < LOCATIONS_PERC[self.location-1]:
            decorated = [(self.opinions[project.category].weight, project) for project in projects_list]
            decorated.sort(reverse=True)
            
            dic_return[decorated[0][1]] = int(UNITS_PER_CITIZEN/2)
            dic_return[decorated[1][1]] = int(UNITS_PER_CITIZEN/3)
            dic_return[decorated[2][1]] = int(UNITS_PER_CITIZEN/6)
        
        return dic_return

    def compute_happiness_level(self, approved_projects_list):
        """
            Computes citizen's happiness level based on:
            - Match between approved projects and the citizen's opinions
            
            The matching process is quite simple.
            For every project we test the weight of the opinion of the citizen for the category of project.
            If the citizen have an opinion > 0 for the category, we consider that he agrees with it.
            Otherwise, he disagrees.
            We compute the number of agrees and disagrees and compare them. 
            
            We included another parameters for the computation of the happiness level:
            - Location of the project (A citizen will be more happy if a project approved is in your neighbourhood)
        """
        projects_agreed = 0
        projects_disagreed = 0
        happiness_level = 0
        
        # opinions
        for project in approved_projects_list:
            c_weight = self.opinions[project.category].weight
                        
            if c_weight > 0:
                projects_agreed += 1
            else:
                projects_disagreed += 1
        
        if projects_agreed > projects_disagreed:
            happiness_level = 0.5
        else:
            happiness_level = 0
        
        # location
        number_projects_location = 0
        for project in approved_projects_list:
            if project.location == self.location:
                number_projects_location += 1
        
        if number_projects_location == 1:
            happiness_level += 0.1
        elif number_projects_location == 2:
            happiness_level += 0.3
        elif number_projects_location > 2:
            happiness_level += 0.5
        
        return happiness_level
        
    
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
    def __init__(self, id, location, influence_level, proactivity_level, opinions):
        Citizen.__init__(self, id)
        self.location = location
        self.influence_level = influence_level
        self.proactivity_level = proactivity_level
        self.opinions = opinions
        
    def select_proposals(proposals_list):
        """
            Choose, based on their opinions and on the likes received, proposals which will become projects.
            
            Returns: list of (projects, units)
        """
        
        return []

    def vote_projects_representative(self, projects_list):
        """
            Gets the list of projects and chooses which projects should by approved.
            This process is implemented by the allocation of units in the projects.
            For example: a citizen has 10 units to distribute over 100 projects. 

            He can allocate 10 on only one project or choose 10 projects and allocate 1 unit per project.
            
            Returns: a dictionary (project_id, units)
            units are integers numbers > 0.

            We can add here a variable that measures the political level of interest in the public opinion.
            This is implemented by taking into consideration the number of likes of the projects.
            So a representative that is focused on public issues will be more influenced by the number of likes of the projects.
            For the moment, we consider only one type of representative and the number of voting units is equally distributed
            taking into considerations number of likes and political opinions.

        """
        global UNITS_PER_CITIZEN
        dic_return = {}
        
        projects_list = random.sample(projects_list, int(len(projects_list)*0.4))
        decorated_likes = [(project.likes, project) for project in projects_list]
#        print self.opinions
        decorated_opinions = [(self.opinions[project.category].weight, project) for project in projects_list]
        
        decorated_likes.sort(reverse=True)
        decorated_opinions.sort(reverse=True)
        
        #dic_return[decorated_likes[0][1]] = 3
        #dic_return[decorated_likes[1][1]] = 2
        dic_return[decorated_opinions[0][1]] = 5
        dic_return[decorated_opinions[1][1]] = 3
        dic_return[decorated_opinions[2][1]] = 2

#        print dic_return
        return dic_return

        

#####################################
##### GAME SIMULATION BEGINS HERE  ##
#####################################

def start_game(city):
    number_rounds = 10
    for i in range(number_rounds):
        statistics = simulate_annual_round(city)
        sh = city.compute_social_happiness()
        print "Social Happiness: " + str(sh)
        city.reset()
        city.compute_overall_opinions()
        # save statistics into csv file.
        

def simulate_annual_round(city):
    city.create_random_proposals()
    simulate_sharing_ideas(city, 5)
    city.like_projects(5)
    city.select_proposals()
    city.vote_projects()
    city.vote_projects_representatives()
    city.select_approved_projects()
    #statistics = city.compute_statistics()
    

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

def load_game(file_name=''):
    city = City()
    global NUMBER_CITIZENS
    global EXPECTED_NUMBER_OF_FRIENDS
    if file_name != '':
        citizens = load_graph(file_name)
        city.citizens = citizens
    else:
        citizens = create_graph(NUMBER_CITIZENS, EXPECTED_NUMBER_OF_FRIENDS)
        city.citizens = citizens
        
    choose_representatives(city, NUMBER_REPRESENTATIVES)
    return city

def choose_representatives(city, number_representatives):
    """
        Randomly chooses the representatives of the city
    """
    citizens_reps = random.sample(city.citizens, number_representatives)
    for c in citizens_reps:
        representative = Representative(c.id, c.location, c.influence_level, c.proactivity_level, c.opinions)
        representative.opinions = setup_random_opinions_representatives()
        city.representatives.append(representative)

def setup_random_friends(citizens_list, number_citizens, expected_number_of_friends):
    for citizen in citizens_list:
        number_friends = int(random.uniform(0,expected_number_of_friends*2))
        print "Citizen %d - Friends: %d - Opinions: %d" % (citizen.id, number_friends, len(citizen.opinions))
        
        for i in range(number_friends):
            friend = random.choice(citizens_list)
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
#        idea = Idea(1,"",i, random.uniform(-1,1))
        idea = Idea(1,"",i, -(1-random.expovariate(6)))
        ideas_dic[i] = idea
        
    return ideas_dic

def setup_random_opinions_representatives():
    """
        Return a set of ideas.

    """
    global CATEGORIES
    
    ideas_dic = {}
    
    for i in CATEGORIES:
        idea = Idea(1,"",i, 1-random.expovariate(6))
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
    
        
def create_graph(number_citizens, expected_number_of_friends):
    citizens_list = []
    for i in range(number_citizens):
        citizen = create_random_citizen(i)
        citizens_list.append(citizen)
        
    setup_random_friends(citizens_list, number_citizens, expected_number_of_friends)
    
    return citizens_list
    

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


def save_graph(graph, file_name):
    """
        The graph passed as argument to this function is a list of citizens
    """
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
    city = load_game('network4.sim')
#    save_graph(city.citizens, 'network4.sim')
#    citizens = load_graph('network1.sim')
    
    start_game(city)

if __name__ == '__main__':
	main()

