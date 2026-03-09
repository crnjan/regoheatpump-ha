from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_URL
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.regoheatpump.const import DOMAIN


async def test_user_step_creates_entry(hass):
    """Test successful user step creates config entry."""
    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()

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
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        assert result["type"] == "form"
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_URL: "socket://HOST:5000/"},
        )

    assert result["type"] == "create_entry"
    assert result["title"] == "Rego Heat Pump (socket://host:5000)"
    assert result["data"] == {CONF_URL: "socket://host:5000"}

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
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        assert result["type"] == "form"
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_URL: "socket://host:5000"},
        )

    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "cannot_connect"}

    hp.verify.assert_awaited_once_with(retry=0)
    hp.dispose.assert_awaited_once()


async def test_user_step_aborts_if_already_configured(hass):
    """Test duplicate normalized URL is rejected."""
    existing_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rego Heat Pump (socket://host:5000)",
        data={CONF_URL: "socket://host:5000"},
    )
    existing_entry.add_to_hass(hass)

    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()

    with patch(
        "custom_components.regoheatpump.config_flow.HeatPump.connect",
        return_value=hp,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_URL: "socket://HOST:5000/"},
        )

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured"

    hp.verify.assert_awaited_once_with(retry=0)
    hp.dispose.assert_awaited_once()


async def test_reconfigure_shows_form_with_existing_value(hass):
    """Test reconfigure starts with form."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rego Heat Pump (socket://old-host:5000)",
        data={CONF_URL: "socket://old-host:5000"},
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


async def test_reconfigure_updates_entry(hass):
    """Test reconfigure updates URL."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rego Heat Pump (socket://old-host:5000)",
        data={CONF_URL: "socket://old-host:5000"},
    )
    entry.add_to_hass(hass)

    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()

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
            user_input={CONF_URL: "socket://NEW-HOST:5000/"},
        )

    assert result["type"] == "abort"
    assert result["reason"] == "reconfigure_successful"

    updated_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert updated_entry is not None
    assert updated_entry.data == {CONF_URL: "socket://new-host:5000"}

    hp.verify.assert_awaited_once_with(retry=0)
    hp.dispose.assert_awaited_once()


async def test_reconfigure_rejects_other_existing_entry(hass):
    """Test reconfigure aborts if URL belongs to another entry."""
    entry_a = MockConfigEntry(
        domain=DOMAIN,
        title="A",
        data={CONF_URL: "socket://a:5000"},
    )
    entry_a.add_to_hass(hass)

    entry_b = MockConfigEntry(
        domain=DOMAIN,
        title="B",
        data={CONF_URL: "socket://b:5000"},
    )
    entry_b.add_to_hass(hass)

    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()

    with patch(
        "custom_components.regoheatpump.config_flow.HeatPump.connect",
        return_value=hp,
    ):
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
            user_input={CONF_URL: "socket://B:5000/"},
        )

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured"

    unchanged_entry = hass.config_entries.async_get_entry(entry_a.entry_id)
    assert unchanged_entry is not None
    assert unchanged_entry.data == {CONF_URL: "socket://a:5000"}

    hp.verify.assert_awaited_once_with(retry=0)
    hp.dispose.assert_awaited_once()


async def test_user_step_unexpected_error(hass):
    """Test config flow handles unexpected exception."""
    hp = MagicMock()
    hp.verify = AsyncMock(side_effect=RuntimeError("boom"))
    hp.dispose = AsyncMock()

    with patch(
        "custom_components.regoheatpump.config_flow.HeatPump.connect",
        return_value=hp,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_URL: "socket://host:5000"},
        )

    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "unknown"}

    hp.dispose.assert_awaited_once()