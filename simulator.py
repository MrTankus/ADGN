import matplotlib
matplotlib.use('TkAgg')

from network import InterestArea
from geometry import Point

from ga import GA

interest_areas = [
    InterestArea(center=Point(0, 0), radius=0.5, name='HUB', is_hub=True),
    InterestArea(center=Point(1, 0.5), radius=0.5, name='Omega1'),
    InterestArea(center=Point(2, 0), radius=0.5, name='Omeg2'),
    InterestArea(center=Point(1, -0.5), radius=0.5, name='Omega3'),
]


ga = GA(interest_areas=interest_areas, initial_population_size=5, generations=18)
fig_id = 1
agents = sorted(ga.agents, key=lambda agent: agent.fitness, reverse=True)
for agent in agents:
    network = agent.network
    network.plot(fig_id=fig_id, xlims=[-7, 7], ylims=[-7, 7])
    fig_id += 1
ga.evolve()
agents = sorted(ga.agents, key=lambda agent: agent.fitness, reverse=True)
network = agents[0].network
network.plot(fig_id=fig_id, xlims=[-7, 7], ylims=[-7, 7])

