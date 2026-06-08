export interface SensorReading {
    sensor_id: string,
    timestamp: Date,
    temperature: number,
    humidity: number,
    pressure: number,
    location: string,
    anomalies: Array<object>
}
