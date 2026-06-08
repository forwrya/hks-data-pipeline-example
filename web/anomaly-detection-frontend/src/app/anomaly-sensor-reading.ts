import { AnomalyInfo } from "./anomaly-info";

export interface AnomalySensorReading extends AnomalyInfo {
    sensor_id: string,
    timestamp: Date,
    temperature: number,
    humidity: number,
    pressure: number,
    location: string
}
