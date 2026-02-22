# Rego Heat Pump Home Assistant Integration

[![GitHub Release](https://img.shields.io/github/v/release/crnjan/regoheatpump-ha.svg)](https://github.com/crnjan/regoheatpump-ha/releases)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5?logo=home-assistant&logoColor=white)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
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

## 📦 Installation (HACS Recommended)

### Install via HACS

1. Open **HACS**
2. Go to **Integrations**
3. Click **⋮ → Custom repositories**
4. Add this repository URL
5. Select **Integration** as the category
6. Click **Install**
7. Restart Home Assistant
8. Go to **Settings → Devices & Services → Add Integration**
9. Search for **Rego Heat Pump**

---

## ⚙️ Configuration

After installation:

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Rego Heat Pump**
4. Enter your serial device (e.g. `socket://192.168.1.100:9500`)
5. Complete the setup wizard

No YAML configuration required.

---

## 🔧 Requirements

- Rego 6xx controller  
- Serial connection to the Home Assistant host  
  (USB-RS485 or compatible serial adapter)  
- HACS (recommended for installation)  

---

## 📊 Supported Entities

### 🌡️ Temperature Sensors (`sensor`)

| Entity ID | Description | Access |
|-----------|------------|--------|
| `sensor.radiator_return` | Radiator return temperature | R |
| `sensor.radiator_forward` | Radiator forward temperature | R |
| `sensor.outdoor` | Outdoor temperature | R |
| `sensor.indoor` | Indoor temperature | R |
| `sensor.hot_water` | Domestic hot water temperature | R |
| `sensor.external_hot_water` | External hot water temperature | R |
| `sensor.compressor_temp` | Compressor temperature | R |
| `sensor.heat_fluid_out` | Heat fluid out temperature | R |
| `sensor.heat_fluid_in` | Heat fluid in temperature | R |
| `sensor.cold_fluid_in` | Cold fluid in temperature | R |
| `sensor.cold_fluid_out` | Cold fluid out temperature | R |

---

### 🎛 Control Values (`number`)

| Entity ID | Description | Access |
|-----------|------------|--------|
| `number.radiator_return_target` | Radiator return target | R |
| `number.radiator_return_on` | Radiator return ON threshold | R |
| `number.radiator_return_off` | Radiator return OFF threshold | R |
| `number.hot_water_on` | Hot water ON threshold | R |
| `number.hot_water_off` | Hot water OFF threshold | R |
| `number.radiator_forward_target` | Radiator forward target | R |
| `number.hot_water_target` | Hot water target temperature | RW |
| `number.hot_water_target_hysteresis` | Hot water hysteresis | RW |
| `number.heat_curve` | Heat curve value | RW |
| `number.heat_curve_fine_adj` | Heat curve fine adjustment | RW |
| `number.heat_curve_2` | Secondary heat curve | RW |
| `number.heat_curve_2_fine_adj` | Secondary heat curve fine adjustment | RW |
| `number.indoor_temp_setting` | Indoor temperature setting | RW |
| `number.curve_infl_by_in_temp` | Curve influence by indoor temp | RW |
| `number.adj_curve_at_20` | Curve adjustment at 20°C | RW |
| `number.adj_curve_at_15` | Curve adjustment at 15°C | RW |
| `number.adj_curve_at_10` | Curve adjustment at 10°C | RW |
| `number.adj_curve_at_5` | Curve adjustment at 5°C | RW |
| `number.adj_curve_at_0` | Curve adjustment at 0°C | RW |
| `number.adj_curve_at_minus5` | Curve adjustment at -5°C | RW |
| `number.adj_curve_at_minus10` | Curve adjustment at -10°C | RW |
| `number.adj_curve_at_minus15` | Curve adjustment at -15°C | RW |
| `number.adj_curve_at_minus20` | Curve adjustment at -20°C | RW |
| `number.adj_curve_at_minus25` | Curve adjustment at -25°C | RW |
| `number.adj_curve_at_minus30` | Curve adjustment at -30°C | RW |
| `number.adj_curve_at_minus35` | Curve adjustment at -35°C | RW |
| `number.heat_curve_coupling_diff` | Heat curve coupling difference | RW |
| `number.summer_disconnection` | Summer disconnection temperature | RW |
| `number.add_heat_power` | Additional heat power (%) | R |

---

### 🔄 Switches (`switch`)

| Entity ID | Description | Access |
|-----------|------------|--------|
| `switch.power_lamp` | Power indicator lamp | R |
| `switch.heat_pump_lamp` | Heat pump active lamp | R |
| `switch.additional_heat_lamp` | Additional heat lamp | R |
| `switch.hot_water_lamp` | Hot water lamp | R |
| `switch.alarm_lamp` | Alarm lamp | R |
| `switch.cold_fluid_pump` | Cold fluid pump | R |
| `switch.compressor` | Compressor state | R |
| `switch.additional_heat_3kw` | Additional heat 3kW | R |
| `switch.additional_heat_6kw` | Additional heat 6kW | R |
| `switch.radiator_pump` | Radiator pump | R |
| `switch.heat_fluid_pump` | Heat fluid pump | R |
| `switch.switch_value` | Generic switch value | R |
| `switch.alarm` | Alarm state | R |

---

### ⏱ Operating Time (`sensor`)

| Entity ID | Description | Unit | Access |
|-----------|------------|------|--------|
| `sensor.heatpump_operation_rad` | Heat pump runtime (Radiator) | h | R |
| `sensor.heatpump_operation_dhw` | Heat pump runtime (DHW) | h | R |
| `sensor.addheat_operation_rad` | Additional heat runtime (Radiator) | h | R |
| `sensor.addheat_operation_dhw` | Additional heat runtime (DHW) | h | R |

---

### ⚠ Status Sensors (`sensor`)

| Entity ID | Description | Access |
|-----------|------------|--------|
| `sensor.last_error_timestamp` | Timestamp of last error | R |
| `sensor.last_error_type` | Last error type | R |

---

**Access Legend**

- **R** = Read-only  
- **RW** = Read & Write  

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
