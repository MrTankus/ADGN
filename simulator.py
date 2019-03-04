import matplotlib
matplotlib.use('TkAgg')

from network import InterestArea
from geometry import Point

from ga import generate_initial_population, evolve


interest_areas = [
    InterestArea(center=Point(0, 0), radius=0.5, name='HUB', is_hub=True),
    InterestArea(center=Point(1, 0.5), radius=0.5, name='Omega1'),
    InterestArea(center=Point(2, 0), radius=0.5, name='Omeg2'),
    InterestArea(center=Point(1, -0.5), radius=0.5, name='Omega3'),
]

networks = list(generate_initial_population(interest_areas=interest_areas, initial_population_size=1))
networks[0].plot(fig_id=1, xlims=[-7, 7], ylims=[-7, 7])
network = evolve(networks=networks, generations=10000)
network.plot(fig_id=2, xlims=[-7, 7], ylims=[-7, 7])
