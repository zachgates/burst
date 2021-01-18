__all__ = [
    'ADJUST_POS_AMOUNT_STANDARD', 'ADJUST_POS_AMOUNT_PINPOINT',
    'ADJUST_POS_EVENTS', 'ADJUST_POS_NORTH', 'ADJUST_POS_SOUTH',
    'ADJUST_POS_EAST', 'ADJUST_POS_WEST', 'ADJUST_HPR_AMOUNT_STANDARD'
    'ADJUST_HPR_AMOUNT_PINPOINT', 'ADJUST_HPR_EVENTS', 'ADJUST_HPR_EAST',
    'ADJUST_HPR_WEST', 'ADJUST_SCALE_AMOUNT_STANDARD',
    'ADJUST_SCALE_AMOUNT_PINPOINT', 'ADJUST_SCALE_EVENTS',
    'ADJUST_SCALE_INCREASE', 'ADJUST_SCALE_DECREASE', 'ObjectManager',
]


from typing import Callable, Iterable

from panda3d import core as p3d

from .SelectionManager import SelectionManager


ADJUST_POS_AMOUNT_STANDARD = 'positional_magnitude_standard'
ADJUST_POS_AMOUNT_PINPOINT = 'positional_magnitude_pinpoint'
ADJUST_POS_NORTH = 'event_move_north'
ADJUST_POS_SOUTH = 'event_move_south'
ADJUST_POS_EAST = 'event_move_east'
ADJUST_POS_WEST = 'event_move_west'
ADJUST_POS_EVENTS = [
    ADJUST_POS_NORTH, ADJUST_POS_SOUTH, ADJUST_POS_EAST, ADJUST_POS_WEST]

ADJUST_HPR_AMOUNT_STANDARD = 'rotational_magnitude_standard'
ADJUST_HPR_AMOUNT_PINPOINT = 'rotational_magnitude_pinpoint'
ADJUST_HPR_EAST = 'event_rotate_east'
ADJUST_HPR_WEST = 'event_rotate_west'
ADJUST_HPR_EVENTS = [ADJUST_HPR_EAST, ADJUST_HPR_WEST]

ADJUST_SCALE_AMOUNT_STANDARD = 'scaling_magnitude_standard'
ADJUST_SCALE_AMOUNT_PINPOINT = 'scaling_magnitude_pinpoint'
ADJUST_SCALE_INCREASE = 'event_scale_increase'
ADJUST_SCALE_DECREASE = 'event_scale_decrease'
ADJUST_SCALE_EVENTS = [ADJUST_SCALE_INCREASE, ADJUST_SCALE_DECREASE]


class ObjectManager(SelectionManager):

    p3d.load_prc_file_data(
        """
        Config defaults from the ObjectManager.
        """,
        f"""
        {ADJUST_POS_AMOUNT_STANDARD} 5.0
        {ADJUST_POS_AMOUNT_PINPOINT} 1.0

        {ADJUST_POS_NORTH} arrow_up
        {ADJUST_POS_SOUTH} arrow_down
        {ADJUST_POS_EAST} arrow_right
        {ADJUST_POS_WEST} arrow_left

        {ADJUST_HPR_AMOUNT_STANDARD} 30.0
        {ADJUST_HPR_AMOUNT_PINPOINT} 15.0

        {ADJUST_HPR_EAST} d
        {ADJUST_HPR_WEST} a

        {ADJUST_SCALE_AMOUNT_STANDARD} 0.5
        {ADJUST_SCALE_AMOUNT_PINPOINT} 0.2

        {ADJUST_SCALE_INCREASE} w
        {ADJUST_SCALE_DECREASE} s
        """,
        )

    def accept_all(self):
        """
        Start listening for all update events.
        """
        super().accept_all()
        self.accept_positional_events()
        self.accept_rotational_events()
        self.accept_scaling_events()

    def accept_positional_events(self):
        """
        Start listening for positional update events.
        """
        self.__accept_events(ADJUST_POS_EVENTS, self._adjust_position)

    def accept_rotational_events(self):
        """
        Start listening for rotational update events.
        """
        self.__accept_events(ADJUST_HPR_EVENTS, self._adjust_rotation)

    def accept_scaling_events(self):
        """
        Start listening for scaling update events.
        """
        self.__accept_events(ADJUST_SCALE_EVENTS, self._adjust_scaling)

    def __accept_events(self,
                        events: Iterable[str],
                        method: Callable,
                        ) -> None:
        """
        Initializes a group of events, hooked to the specified method.
        """
        for event in events:
            key = p3d.ConfigVariableString(event).get_value()
            self.accept(key, method, [event, False])
            self.accept(f'{key}-repeat', method, [event, False])
            self.accept(f'shift-{key}', method, [event, True])
            self.accept(f'shift-{key}-repeat', method, [event, True])

    def __get_magnitude(self, *,
                        precision: bool,
                        standard: str,
                        pinpoint: str = None,
                        ) -> int:
        """
        Accesses PRC config data to return the specified magnitude value.
        Supplying a truthy precision flag indicates that the pinpoint value is
        desired, if possible; otherwise, the standard value will be returned.
        """
        if not isinstance(standard, str):
            raise TypeError('expected string for standard config name')

        if pinpoint and not isinstance(pinpoint, str):
            raise TypeError('expected string for pinpoint config name')

        if precision and pinpoint is not None:
            return p3d.ConfigVariableDouble(pinpoint).get_value()
        else:
            return p3d.ConfigVariableDouble(standard).get_value()

    def _adjust_position(self, event_name: str, precision: bool):
        """
        The positional adjustment event hook (default: arrow keys).
        """
        magnitude = self.__get_magnitude(
            precision = precision,
            standard = ADJUST_POS_AMOUNT_STANDARD,
            pinpoint = ADJUST_POS_AMOUNT_PINPOINT,
            )

        vector_map = {
            ADJUST_POS_NORTH: p3d.Vec3(0, magnitude, 0),
            ADJUST_POS_SOUTH: p3d.Vec3(0, -magnitude, 0),
            ADJUST_POS_EAST: p3d.Vec3(magnitude, 0, 0),
            ADJUST_POS_WEST: p3d.Vec3(-magnitude, 0, 0),
        }

        position = self.get_selection().get_pos()
        vector = vector_map.get(event_name, p3d.Vec3.zero())
        self.get_selection().set_pos(position + vector)

    def _adjust_rotation(self, event_name: str, precision: bool):
        """
        The rotational adjustment event hook (default: A/D keys).
        """
        magnitude = self.__get_magnitude(
            precision = precision,
            standard = ADJUST_HPR_AMOUNT_STANDARD,
            pinpoint = ADJUST_HPR_AMOUNT_PINPOINT,
            )

        vector_map = {
            ADJUST_HPR_EAST: p3d.Vec3(magnitude, 0, 0),
            ADJUST_HPR_WEST: p3d.Vec3(-magnitude, 0, 0),
        }

        rotation = self.get_selection().get_hpr()
        vector = vector_map.get(event_name, p3d.Vec3.zero())
        self.get_selection().set_hpr(rotation + vector)

    def _adjust_scaling(self, event_name: str, precision: bool):
        """
        The scaling adjustment event hook (default: W/S keys).
        """
        magnitude = self.__get_magnitude(
            precision = precision,
            standard = ADJUST_SCALE_AMOUNT_STANDARD,
            pinpoint = ADJUST_SCALE_AMOUNT_PINPOINT,
            )

        vector_map = {
            ADJUST_SCALE_INCREASE: magnitude,
            ADJUST_SCALE_DECREASE: -magnitude,
        }

        scale = self.get_selection().get_scale()
        vector = 1.0 + vector_map.get(event_name, 0.0)
        self.get_selection().set_scale(scale * vector)
        self.get_selection().adjust_center()
