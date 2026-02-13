# Rego Heat Pump Integration

## The Rego 6xx family

The Rego 6xx controllers family is used in many heat pumps such as IVT/Bosch/Autotherm/Carrier and others.

The Rego 6xx unit contains an interface marked as service.
Header of this interface is close to the control unit.
This is a 5V (TTL) serial interface and is connected by a 9-pin CAN/D-sub connector.
Pinout:

2 - RxD
3 - TxD
4 - +5V
5 - GND

Serial communication is using 19200 bps, 8 bit, no parity, 1 stop bit.

### Channels

Below is the list of supported entities:

| Channel Type ID                       | Item Type   | Access |
|---------------------------------------|-------------|--------|
| sensorValues#radiatorReturn           | Temperature | R      |
| sensorValues#outdoor                  | Temperature | R      |
| sensorValues#hotWater                 | Temperature | R      |
| sensors#radiatorForward               | Temperature | R      |
| sensorValues#indoor                   | Temperature | R      |
| sensorValues#compressor               | Temperature | R      |
| sensorValues#heatFluidOut             | Temperature | R      |
| sensorValues#heatFluidIn              | Temperature | R      |
| sensorValues#coldFluidIn              | Temperature | R      |
| sensorValues#coldFluidOut             | Temperature | R      |
| sensorValues#externalHotWater         | Temperature | R      |
| status#lastErrorTimestamp             | DateTime    | R      |
| status#lastErrorType                  | String      | R      |
| frontPanel#powerLamp                  | Switch      | R      |
| frontPanel#heatPumpLamp               | Switch      | R      |
| frontPanel#additionalHeatLamp         | Switch      | R      |
| frontPanel#hotWaterLamp               | Switch      | R      |
| frontPanel#alarmLamp                  | Switch      | R      |
| controlData#radiatorReturnTarget      | Temperature | R      |
| controlData#radiatorReturnOn          | Temperature | R      |
| controlData#radiatorReturnOff         | Temperature | R      |
| controlData#hotWaterOn                | Temperature | R      |
| controlData#hotWaterOff               | Temperature | R      |
| controlData#radiatorForwardTarget     | Temperature | R      |
| controlData#addHeatPower              | Number (%)  | R      |
| deviceValues#coldFluidPump            | Switch      | R      |
| deviceValues#compressor               | Switch      | R      |
| deviceValues#additionalHeat3kW        | Switch      | R      |
| deviceValues#additionalHeat6kW        | Switch      | R      |
| deviceValues#radiatorPump             | Switch      | R      |
| deviceValues#heatFluidPump            | Switch      | R      |
| deviceValues#switchValue              | Switch      | R      |
| deviceValues#alarm                    | Switch      | R      |
| settings#hotWaterTarget               | Temperature | RW     |
| settings#hotWaterTargetHysteresis     | Temperature | RW     |
| settings#heatCurve                    | Number      | RW     |
| settings#heatCurveFineAdj             | Temperature | RW     |
| settings#heatCurve2                   | Number      | RW     |
| settings#heatCurve2FineAdj            | Temperature | RW     |
| settings#indoorTempSetting            | Temperature | RW     |
| settings#curveInflByInTemp            | Number      | RW     |
| settings#adjCurveAt20                 | Temperature | RW     |
| settings#adjCurveAt15                 | Temperature | RW     |
| settings#adjCurveAt10                 | Temperature | RW     |
| settings#adjCurveAt5                  | Temperature | RW     |
| settings#adjCurveAt0                  | Temperature | RW     |
| settings#adjCurveAtMinus5             | Temperature | RW     |
| settings#adjCurveAtMinus10            | Temperature | RW     |
| settings#adjCurveAtMinus15            | Temperature | RW     |
| settings#adjCurveAtMinus20            | Temperature | RW     |
| settings#adjCurveAtMinus25            | Temperature | RW     |
| settings#adjCurveAtMinus30            | Temperature | RW     |
| settings#adjCurveAtMinus35            | Temperature | RW     |
| settings#heatCurveCouplingDiff        | Temperature | RW     |
| settings#summerDisconnection          | Temperature | RW     |
| operatingTimes#heatPumpInOperationRAD | Hours       | R      |
| operatingTimes#heatPumpInOperationDHW | Hours       | R      |
| operatingTimes#addHeatInOperationRAD  | Hours       | R      |
| operatingTimes#addHeatInOperationDHW  | Hours       | R      |

Access: R = read only; RW = read write
