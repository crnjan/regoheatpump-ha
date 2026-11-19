"""Helpers for creating common register definitions."""

from ..composite_register import CompositeRegister
from ..compositions import Compositions
from ..decoders import Decoders
from ..identifier import Identifier
from ..register import Register
from ..single_register import SingleRegister
from ..sources import Sources
from ..transformations import Transformations
from ..type import Type


class RegisterFactory:
    """Factory for typed register instances."""

    @staticmethod
    def version(identifier: Identifier) -> Register:
        """Create the version register."""
        return SingleRegister(
            identifier=identifier,
            source=Sources.VERSION,
            address=0x0000,
            decoder=Decoders.INT_16,
            transformation=Transformations.IDENTITY,
            type=Type.VERSION,
        )

    @staticmethod
    def last_error(identifier: Identifier) -> Register:
        """Create the last error register."""
        return SingleRegister(
            identifier=identifier,
            source=Sources.LAST_ERROR,
            address=0x0000,
            decoder=Decoders.ERROR,
            transformation=Transformations.IDENTITY,
            type=Type.ERROR,
        )

    @staticmethod
    def real_time_clock(identifier: Identifier) -> Register:
        """Create the real-time clock from its BCD front panel registers.

        The seconds come first: the time of reading is taken just before.
        Register 6 (weekday) is not needed.
        """
        fields = (
            ("second", 0x0001),
            ("minute", 0x0002),
            ("hour", 0x0003),
            ("date", 0x0004),
            ("month", 0x0005),
            ("year", 0x0007),
        )
        return CompositeRegister(
            identifier=identifier,
            type=Type.CLOCK,
            parts=tuple(
                SingleRegister(
                    identifier=Identifier(
                        id=f"{identifier.id}_{name}", group=identifier.group
                    ),
                    source=Sources.FRONT_PANEL,
                    address=address,
                    decoder=Decoders.UINT_16,
                    transformation=Transformations.BCD,
                    type=Type.UNITLESS,
                )
                for name, address in fields
            ),
            composition=Compositions.DATE_TIME,
        )

    @staticmethod
    def front_panel_switch(identifier: Identifier, address: int) -> Register:
        """Create a front panel switch register."""
        return SingleRegister(
            identifier=identifier,
            source=Sources.FRONT_PANEL,
            address=address,
            decoder=Decoders.INT_16,
            transformation=Transformations.IDENTITY,
            type=Type.SWITCH,
        )

    @staticmethod
    def system_temperature(
        identifier: Identifier, address: int, is_writable: bool = False
    ) -> Register:
        """Create a system temperature register."""
        return SingleRegister(
            identifier=identifier,
            source=Sources.SYSTEM,
            address=address,
            decoder=Decoders.INT_16,
            transformation=Transformations.NUMERIC_ONE_TENTH,
            type=Type.TEMPERATURE,
            is_writable=is_writable,
        )

    @staticmethod
    def system_unitless(
        identifier: Identifier, address: int, is_writable: bool = False
    ) -> Register:
        """Create a unitless system register."""
        return SingleRegister(
            identifier=identifier,
            source=Sources.SYSTEM,
            address=address,
            decoder=Decoders.INT_16,
            transformation=Transformations.NUMERIC_ONE_TENTH,
            type=Type.UNITLESS,
            is_writable=is_writable,
        )

    @staticmethod
    def system_integer(
        identifier: Identifier, address: int, is_writable: bool = False
    ) -> Register:
        """Create a unitless system register holding a whole number."""
        return SingleRegister(
            identifier=identifier,
            source=Sources.SYSTEM,
            address=address,
            decoder=Decoders.INT_16,
            transformation=Transformations.INTEGER,
            type=Type.UNITLESS,
            is_writable=is_writable,
        )

    @staticmethod
    def system_switch(identifier: Identifier, address: int) -> Register:
        """Create a system switch register."""
        return SingleRegister(
            identifier=identifier,
            source=Sources.SYSTEM,
            address=address,
            decoder=Decoders.INT_16,
            transformation=Transformations.IDENTITY,
            type=Type.SWITCH,
        )

    @staticmethod
    def system_hours(identifier: Identifier, address: int) -> Register:
        """Create a system hours register."""
        return SingleRegister(
            identifier=identifier,
            source=Sources.SYSTEM,
            address=address,
            decoder=Decoders.UINT_16,
            transformation=Transformations.IDENTITY,
            type=Type.HOURS,
        )
