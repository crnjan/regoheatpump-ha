# Rego Heat Pump Home Assistant Integration

[![GitHub Release](https://img.shields.io/github/v/release/crnjan/regoheatpump-ha.svg)](https://github.com/crnjan/regoheatpump-ha/releases)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5?logo=home-assistant&logoColor=white)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS%20%7C%20Marketplace-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant Validation](https://github.com/crnjan/regoheatpump-ha/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/crnjan/regoheatpump-ha/actions/workflows/hassfest.yaml)
[![HACS Validation](https://github.com/crnjan/regoheatpump-ha/actions/workflows/hacs_validate.yml/badge.svg)](https://github.com/crnjan/regoheatpump-ha/actions/workflows/hacs_validate.yml)

Custom Home Assistant integration for **Rego 6xx heat pump controllers**.

This integration provides local monitoring and control of your heat pump via serial communication — no cloud required.

---

## ✨ Features

### 🔎 Monitoring

- Heat pump operational status  
- Supply and return temperatures  
- Domestic hot water temperature  
- Operating modes  
- Alarm and fault indicators  
- Operating hour counters  

### 🎛 Control

- Set domestic hot water temperature  
- Adjust heating curve parameters  
- Modify selected controller settings  
- Direct control from the Home Assistant UI  

### 🔌 Local & Reliable

- Direct serial communication  
- No internet dependency  
- Asynchronous polling  
- Native Config Flow support  

---

## 📦 Installation

Requires **Home Assistant 2026.5.0** or newer.

### Home Assistant 2026.11 and newer (Marketplace)

1. Go to **Settings → Marketplace**
2. Select **Add from link** (upper-right corner)
3. Enter `crnjan/regoheatpump-ha` and select **Add**  
   (custom repositories require a connected GitHub account; if asked for a type, choose **Integration**)
4. Open **Rego Heat Pump** and select **Install**, then confirm
5. Continue with the setup dialog, or later go to **Settings → Devices & Services → Add Integration** and search for **Rego Heat Pump**

### Home Assistant 2026.5 – 2026.10 (HACS)

1. Open **HACS**
2. Click **⋮ → Custom repositories**
3. Add `https://github.com/crnjan/regoheatpump-ha`
4. Select **Integration** as the category
5. Find **Rego Heat Pump** and click **Download**
6. Restart Home Assistant
7. Go to **Settings → Devices & Services → Add Integration**
8. Search for **Rego Heat Pump**

### Updating

Updates appear in the Marketplace (or HACS). A restart of Home Assistant is required after updating.

---

## ⚙️ Configuration

After installation:

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Rego Heat Pump**
4. Enter the connection URL of your serial device (see examples below)
5. Complete the setup wizard

No YAML configuration required.

### Connection URL examples

| Connection | Example URL |
|---|---|
| Local serial adapter | `/dev/ttyUSB0` or `/dev/serial/by-id/usb-FTDI_…` |
| Serial-to-network bridge (raw TCP) | `socket://192.168.1.100:9500` |
| RFC 2217 server | `rfc2217://192.168.1.100:4000` |
| [ESPHome serial proxy](https://esphome.io/components/serial_proxy/) | `esphome://heatpump.local/?port_name=rego&key=<api-encryption-key>` |

For the ESPHome serial proxy:

- `port_name` is the name of the serial proxy in your ESPHome config, and `key` is the device's API encryption key. The API port defaults to 6053.
- URL-encode the key, as it usually contains `+`, `/` or `=` (`+` → `%2B`, `/` → `%2F`, `=` → `%3D`).

---

## 📊 Supported Entities

Entity IDs below assume the default device name **Heat Pump**. Home Assistant creates them when the integration is first set up, so they may differ if you renamed the device or entities. Entities not enabled by default can be enabled under **Settings → Devices & Services → Entities**.

### 🌡️ Temperatures (`sensor`)

| Entity ID | Name | Enabled by default |
|---|---|:---:|
| `sensor.heat_pump_radiator_return` | Radiator return | ✅ |
| `sensor.heat_pump_outdoor` | Outdoor | ✅ |
| `sensor.heat_pump_dhw` | DHW | ✅ |
| `sensor.heat_pump_radiator_forward` | Radiator forward | ✅ |
| `sensor.heat_pump_indoor` | Indoor |  |
| `sensor.heat_pump_compressor` | Compressor | ✅ |
| `sensor.heat_pump_heat_fluid_out` | Heat fluid out | ✅ |
| `sensor.heat_pump_heat_fluid_in` | Heat fluid in | ✅ |
| `sensor.heat_pump_cold_fluid_in` | Cold fluid in | ✅ |
| `sensor.heat_pump_cold_fluid_out` | Cold fluid out | ✅ |
| `sensor.heat_pump_dhw_external` | DHW external (Rego 637 only) | ✅ |

---

### 🎯 Control values (`sensor`)

Values calculated by the controller (read-only).

| Entity ID | Name | Enabled by default |
|---|---|:---:|
| `sensor.heat_pump_radiator_forward_target` | Radiator forward target | ✅ |
| `sensor.heat_pump_radiator_return_target` | Radiator return target |  |
| `sensor.heat_pump_radiator_return_on` | Radiator return on | ✅ |
| `sensor.heat_pump_radiator_return_off` | Radiator return off | ✅ |
| `sensor.heat_pump_dhw_on` | DHW on | ✅ |
| `sensor.heat_pump_dhw_off` | DHW off | ✅ |

---

### 🎛 Settings (`number`)

Writable controller settings.

| Entity ID | Name | Range | Enabled by default |
|---|---|---|:---:|
| `number.heat_pump_heat_curve` | Heat curve | 0 … 10 | ✅ |
| `number.heat_pump_heat_curve_fine_tune` | Heat curve fine tune | -10 … 10 | ✅ |
| `number.heat_pump_heat_curve_coupling_diff` | Heat curve coupling diff | 2 … 15 |  |
| `number.heat_pump_heat_curve_2` | Heat curve 2 | 0 … 10 |  |
| `number.heat_pump_heat_curve_2_fine_tune` | Heat curve 2 fine tune | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_20_degc` | Adjust heat curve at 20 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_15_degc` | Adjust heat curve at 15 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_10_degc` | Adjust heat curve at 10 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_5_degc` | Adjust heat curve at 5 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_0_degc` | Adjust heat curve at 0 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_minus_5_degc` | Adjust heat curve at minus 5 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_minus_10_degc` | Adjust heat curve at minus 10 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_minus_15_degc` | Adjust heat curve at minus 15 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_minus_20_degc` | Adjust heat curve at minus 20 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_minus_25_degc` | Adjust heat curve at minus 25 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_minus_30_degc` | Adjust heat curve at minus 30 °C | -10 … 10 |  |
| `number.heat_pump_adjust_heat_curve_at_minus_35_degc` | Adjust heat curve at minus 35 °C | -10 … 10 |  |
| `number.heat_pump_indoor_target` | Indoor target | 10 … 30 |  |
| `number.heat_pump_indoor_sensor_influence` | Indoor sensor influence | -10 … 10 |  |
| `number.heat_pump_summer_disconnection` | Summer disconnection | 10 … 30 | ✅ |
| `number.heat_pump_dhw_target` | DHW target | 35 … 54 | ✅ |
| `number.heat_pump_dhw_hysteresis` | DHW hysteresis | 2 … 15 | ✅ |

---

### 🔄 Device states (`binary_sensor`)

| Entity ID | Name | Enabled by default |
|---|---|:---:|
| `binary_sensor.heat_pump_cold_fluid_pump` | Cold fluid pump | ✅ |
| `binary_sensor.heat_pump_compressor` | Compressor | ✅ |
| `binary_sensor.heat_pump_additional_heat_3kw` | Additional heat 3kW | ✅ |
| `binary_sensor.heat_pump_additional_heat_6kw` | Additional heat 6kW | ✅ |
| `binary_sensor.heat_pump_radiator_pump` | Radiator pump | ✅ |
| `binary_sensor.heat_pump_heat_fluid_pump` | Heat fluid pump | ✅ |
| `binary_sensor.heat_pump_switch_valve` | Switch valve | ✅ |
| `binary_sensor.heat_pump_alarm` | Alarm | ✅ |

---

### 💡 Front panel lamps (`binary_sensor`)

| Entity ID | Name | Enabled by default |
|---|---|:---:|
| `binary_sensor.heat_pump_power_lamp` | Power lamp |  |
| `binary_sensor.heat_pump_heat_pump_lamp` | Heat pump lamp |  |
| `binary_sensor.heat_pump_additional_heat_lamp` | Additional heat lamp |  |
| `binary_sensor.heat_pump_dhw_lamp` | DHW lamp |  |
| `binary_sensor.heat_pump_alarm_lamp` | Alarm lamp |  |

---

### ⏱ Operating times (`sensor`, hours)

| Entity ID | Name | Enabled by default |
|---|---|:---:|
| `sensor.heat_pump_hp_in_oper_radiators` | HP in oper. - radiators | ✅ |
| `sensor.heat_pump_hp_in_oper_dhw` | HP in oper. - DHW | ✅ |
| `sensor.heat_pump_add_heat_in_oper_radiators` | Add. heat in oper. - radiators | ✅ |
| `sensor.heat_pump_add_heat_in_oper_dhw` | Add. heat in oper. - DHW | ✅ |

---

### ⚠ Last error (`sensor`)

The state is the error code (shown as its description in the UI); the `timestamp` attribute holds when it occurred.

| Entity ID | Name | Enabled by default |
|---|---|:---:|
| `sensor.heat_pump_last_error` | Last error | ✅ |

---

## 🔗 Resources

The following resources provide detailed technical information about how to connect to Rego 6xx based heat pumps, including serial interface details, communication protocols, and hardware considerations.

- 🔧 **Rego600 Heat Pump Controller Interface (SourceForge)**  
  Documentation and tools related to the Rego600/6xx communication interface, including protocol insights and serial communication details.  
  https://rago600.sourceforge.io/

- 💬 **openHAB Community – Rego 6xx Based Heat Pumps**  
  Community discussion and implementation details for connecting to Rego 6xx controllers. Includes practical setup examples and parameter access information.  
  https://community.openhab.org/t/new-binding-rego-6xx-based-heat-pumps/17219

---

## 🔌 Hardware Connection Summary

Most Rego 6xx controllers expose a service serial interface used for diagnostics and control.

Typical communication parameters:

- **Interface type:** TTL serial (⚠ not full RS232 voltage levels)
- **Baud rate:** 19200 bps  
- **Data format:** 8N1 (8 data bits, no parity, 1 stop bit)  
- **Protocol:** Proprietary polling-based protocol  

---

## ⚠ Disclaimer

This is an independent, personal project and is not affiliated with or endorsed by any manufacturer.

The software is provided "AS IS", without warranty of any kind. Use of this integration and connection to your heat pump controller is entirely at your own risk.

The author assumes no liability for any damage, malfunction, data loss, warranty voidance, or other consequences resulting from its use. You are solely responsible for verifying correct wiring, voltage levels, and configuration before connecting to your equipment.
