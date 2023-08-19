__all__ = [
    'CharacterAI',
]


from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI


class CharacterAI(DistributedSmoothNodeAI):
    def generate(self):
        super().generate()
        print('new CharacterAI')
