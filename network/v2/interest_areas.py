import hashlib
import uuid
import json
import random
from geometry.shapes import Circle


class InterestArea(Circle):

    def __init__(self, center, radius, name, is_hub=False):
        super(InterestArea, self).__init__(center=center, radius=radius)
        self.name = name
        self.is_hub = is_hub

    def as_json_dict(self, *args, **kwargs):
        return {
            'name': self.name,
            'center': self.center,
            'radius': self.radius,
            'is_hub': self.is_hub
        }

    @classmethod
    def from_json(cls, ia_json):
        return InterestArea(center=tuple(ia_json['center']), radius=ia_json['radius'], name=ia_json['name'], is_hub=ia_json['is_hub'])


class InterestAreaGenerator(object):

    @classmethod
    def from_file(cls, file_name):
        interest_areas = set()
        with open(file_name, 'r') as file:
            json_string = file.read()
            if json_string:
                ias_list = json.loads(json_string)
                hub_count = 0
                for ia_dict in ias_list:
                    is_hub = ia_dict.get('is_hub', False)
                    if is_hub:
                        hub_count += 1
                        ia_name = 'HUB_' + str(hub_count)
                    else:
                        ia_name = ia_dict.get('name', hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:6])
                    interest_areas.add(InterestArea(center=tuple(ia_dict['center']),
                                                    radius=ia_dict['radius'],
                                                    name=ia_name,
                                                    is_hub=is_hub))
        return interest_areas

    @classmethod
    def random(cls, amount, xlims, ylims, allow_overlapping):
        interest_areas = set()
        interest_area_id = 1
        while len(interest_areas) < amount:
            ia = InterestArea(center=((xlims[0] + 1) + (xlims[1] - 1 - xlims[0] - 1) * random.random(),
                                      (ylims[0] + 1) + (ylims[1] - 1 - ylims[0] - 1) * random.random()),
                              radius=0.3 + 0.2 * random.random(), name='IA-' + str(interest_area_id))
            if not allow_overlapping:
                if not any(other.intersects(ia) for other in interest_areas):
                    interest_areas.add(ia)
                    interest_area_id += 1
            else:
                interest_areas.add(ia)
                interest_area_id += 1

        hub = random.sample(interest_areas, 1)[0]
        hub.name = 'HUB'
        hub.is_hub = True

        return interest_areas
