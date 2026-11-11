from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant import config_entries
from homeassistant.const import CONF_URL
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.regoheatpump.config_flow import normalize_connection_url
from custom_components.regoheatpump.const import (
    CONF_REGO_TYPE,
    DEFAULT_REGO_TYPE,
    DOMAIN,
)
from custom_components.regoheatpump.rego600 import RegoType


async def test_user_step_creates_entry(hass):
    """Test successful user step creates config entry."""
    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()

    with (
        patch(
            "custom_components.regoheatpump.config_flow.HeatPump.connect",
            return_value=hp,
        ) as mock_connect,
        patch(
            "custom_components.regoheatpump.async_setup_entry",
            return_value=True,
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        assert result["type"] == "form"
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_URL: "socket://HOST:5000/",
                CONF_REGO_TYPE: RegoType.REGO637.value,
            },
        )

    assert result["type"] == "create_entry"
    assert result["title"] == "Rego Heat Pump (Rego 637, socket://host:5000)"
    assert result["data"] == {
        CONF_URL: "socket://host:5000",
        CONF_REGO_TYPE: RegoType.REGO637.value,
    }

    mock_connect.assert_called_once_with(
        url="socket://host:5000",
        rego_type=RegoType.REGO637,
    )
    hp.verify.assert_awaited_once_with(retry=0)
    hp.dispose.assert_awaited_once()


async def test_user_step_cannot_connect(hass):
    """Test config flow handles connection failure."""
    hp = MagicMock()
    hp.verify = AsyncMock(side_effect=OSError("timeout"))
    hp.dispose = AsyncMock()

    with patch(
        "custom_components.regoheatpump.config_flow.HeatPump.connect",
        return_value=hp,
    ) as mock_connect:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        assert result["type"] == "form"
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_URL: "socket://host:5000",
                CONF_REGO_TYPE: RegoType.REGO636.value,
            },
        )

    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "cannot_connect"}

    mock_connect.assert_called_once_with(
        url="socket://host:5000",
        rego_type=RegoType.REGO636,
    )
    hp.verify.assert_awaited_once_with(retry=0)
    hp.dispose.assert_awaited_once()


async def test_user_step_aborts_if_already_configured(hass):
    """Test duplicate normalized URL is rejected."""
    existing_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rego Heat Pump (socket://host:5000)",
        data={
            CONF_URL: "socket://host:5000",
            CONF_REGO_TYPE: RegoType.REGO637.value,
        },
    )
    existing_entry.add_to_hass(hass)

    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()

    with patch(
        "custom_components.regoheatpump.config_flow.HeatPump.connect",
        return_value=hp,
    ) as mock_connect:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_URL: "socket://HOST:5000/",
                CONF_REGO_TYPE: RegoType.REGO636.value,
            },
        )

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured"

    mock_connect.assert_not_called()
    hp.verify.assert_not_called()
    hp.dispose.assert_not_called()


async def test_reconfigure_shows_form_with_existing_value(hass):
    """Test reconfigure starts with form."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rego Heat Pump (socket://old-host:5000)",
        data={
            CONF_URL: "socket://old-host:5000",
            CONF_REGO_TYPE: RegoType.REGO636.value,
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )

    assert result["type"] == "form"
    assert result["step_id"] == "reconfigure"

    schema_defaults = {
        k.schema: (k.default() if callable(k.default) else k.default)
        for k in result["data_schema"].schema
        if hasattr(k, "default")
    }
    assert schema_defaults[CONF_URL] == "socket://old-host:5000"
    assert schema_defaults[CONF_REGO_TYPE] == RegoType.REGO636.value


async def test_reconfigure_updates_entry(hass):
    """Test reconfigure updates URL and rego type."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rego Heat Pump (socket://old-host:5000)",
        data={
            CONF_URL: "socket://old-host:5000",
            CONF_REGO_TYPE: RegoType.REGO637.value,
        },
    )
    entry.add_to_hass(hass)

    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()

    with (
        patch(
            "custom_components.regoheatpump.config_flow.HeatPump.connect",
            return_value=hp,
        ) as mock_connect,
        patch(
            "custom_components.regoheatpump.async_setup_entry",
            return_value=True,
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )

        assert result["type"] == "form"
        assert result["step_id"] == "reconfigure"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_URL: "socket://NEW-HOST:5000/",
                CONF_REGO_TYPE: RegoType.REGO636.value,
            },
        )

    assert result["type"] == "abort"
    assert result["reason"] == "reconfigure_successful"

    updated_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert updated_entry is not None
    assert updated_entry.data == {
        CONF_URL: "socket://new-host:5000",
        CONF_REGO_TYPE: RegoType.REGO636.value,
    }

    mock_connect.assert_called_once_with(
        url="socket://new-host:5000",
        rego_type=RegoType.REGO636,
    )
    hp.verify.assert_awaited_once_with(retry=0)
    hp.dispose.assert_awaited_once()


async def test_reconfigure_rejects_other_existing_entry(hass):
    """Test reconfigure aborts if URL belongs to another entry."""
    entry_a = MockConfigEntry(
        domain=DOMAIN,
        title="A",
        data={
            CONF_URL: "socket://a:5000",
            CONF_REGO_TYPE: RegoType.REGO637.value,
        },
    )
    entry_a.add_to_hass(hass)

    entry_b = MockConfigEntry(
        domain=DOMAIN,
        title="B",
        data={
            CONF_URL: "socket://b:5000",
            CONF_REGO_TYPE: RegoType.REGO636.value,
        },
    )
    entry_b.add_to_hass(hass)

    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()

    with patch(
        "custom_components.regoheatpump.config_flow.HeatPump.connect",
        return_value=hp,
    ) as mock_connect:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry_a.entry_id,
            },
        )

        assert result["type"] == "form"
        assert result["step_id"] == "reconfigure"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_URL: "socket://B:5000/",
                CONF_REGO_TYPE: RegoType.REGO637.value,
            },
        )

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured"

    unchanged_entry = hass.config_entries.async_get_entry(entry_a.entry_id)
    assert unchanged_entry is not None
    assert unchanged_entry.data == {
        CONF_URL: "socket://a:5000",
        CONF_REGO_TYPE: RegoType.REGO637.value,
    }

    mock_connect.assert_not_called()
    hp.verify.assert_not_called()
    hp.dispose.assert_not_called()


async def test_user_step_unexpected_error(hass):
    """Test config flow handles unexpected exception."""
    hp = MagicMock()
    hp.verify = AsyncMock(side_effect=RuntimeError("boom"))
    hp.dispose = AsyncMock()

    with patch(
        "custom_components.regoheatpump.config_flow.HeatPump.connect",
        return_value=hp,
    ) as mock_connect:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_URL: "socket://host:5000",
                CONF_REGO_TYPE: DEFAULT_REGO_TYPE,
            },
        )

    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "unknown"}

    mock_connect.assert_called_once_with(
        url="socket://host:5000",
        rego_type=RegoType(DEFAULT_REGO_TYPE),
    )
    hp.dispose.assert_awaited_once()


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("/dev/ttyUSB0", "/dev/ttyUSB0"),
        ("  /dev/serial/by-id/usb-FTDI_AB12  ", "/dev/serial/by-id/usb-FTDI_AB12"),
        ("socket://HOST:5000/", "socket://host:5000"),
        ("SOCKET://Host:5000", "socket://host:5000"),
        (
            "esphome://HeatPump.local/?port_name=Rego&key=AbC%2BdEf%3D",
            "esphome://heatpump.local/?port_name=Rego&key=AbC%2BdEf%3D",
        ),
        (
            "esphome://HeatPump.local:6053/Rego",
            "esphome://heatpump.local:6053/Rego",
        ),
        ("rfc2217://User:Pass@HOST:4000", "rfc2217://User:Pass@host:4000"),
    ],
)
def test_normalize_connection_url(url: str, expected: str) -> None:
    """Only scheme and host are lowercased; path, query and credentials are kept."""
    assert normalize_connection_url(url) == expected


async def _run_flow(hass, source: str, url: str, rego_type: RegoType, entry=None):
    """Run a user or reconfigure flow with a mocked heat pump."""
    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()

    context = {"source": source}
    if entry is not None:
        context["entry_id"] = entry.entry_id

    with (
        patch(
            "custom_components.regoheatpump.config_flow.HeatPump.connect",
            return_value=hp,
        ),
        patch(
            "custom_components.regoheatpump.async_setup_entry",
            return_value=True,
        ),
    ):
        result = await hass.config_entries.flow.async_init(DOMAIN, context=context)
        return await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_URL: url, CONF_REGO_TYPE: rego_type.value},
        )


async def test_user_step_title_hides_encryption_key(hass):
    """The entry title never contains the ESPHome API key; the data keeps it."""
    url = "esphome://HeatPump.local/?port_name=Rego&key=AbC%2BdEf%3D"

    result = await _run_flow(hass, config_entries.SOURCE_USER, url, RegoType.REGO637)

    assert result["type"] == "create_entry"
    assert result["title"] == (
        "Rego Heat Pump (Rego 637, esphome://heatpump.local/?port_name=Rego&key=***)"
    )
    assert result["data"][CONF_URL] == (
        "esphome://heatpump.local/?port_name=Rego&key=AbC%2BdEf%3D"
    )


@pytest.mark.parametrize(
    ("old_title", "expected_title"),
    [
        # Auto-generated title from an older version, containing the key
        (
            "Rego Heat Pump (Rego 637, esphome://hp.local/?key=old)",
            "Rego Heat Pump (Rego 637, esphome://hp.local/?key=***)",
        ),
        # Current auto-generated (redacted) title
        (
            "Rego Heat Pump (Rego 637, esphome://hp.local/?key=***)",
            "Rego Heat Pump (Rego 637, esphome://hp.local/?key=***)",
        ),
        # User renamed the entry: keep their title
        ("My heat pump", "My heat pump"),
    ],
)
async def test_reconfigure_refreshes_generated_title(hass, old_title, expected_title):
    """Reconfigure replaces generated titles but keeps user-chosen ones."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=old_title,
        data={
            CONF_URL: "esphome://hp.local/?key=old",
            CONF_REGO_TYPE: RegoType.REGO637.value,
        },
    )
    entry.add_to_hass(hass)

    result = await _run_flow(
        hass,
        config_entries.SOURCE_RECONFIGURE,
        "esphome://hp.local/?key=new",
        RegoType.REGO637,
        entry,
    )

    assert result["reason"] == "reconfigure_successful"
    updated = hass.config_entries.async_get_entry(entry.entry_id)
    assert updated.title == expected_title
    assert updated.data[CONF_URL] == "esphome://hp.local/?key=new"
