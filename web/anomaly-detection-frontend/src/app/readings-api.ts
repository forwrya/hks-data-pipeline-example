import { Service } from '@angular/core';
import { SensorReading } from './sensorreading';
import { environment } from '../environments/environment';
import moment from 'moment';

@Service()
export class ReadingsAPI {
    async getRecentAnomalies(): Promise<SensorReading[]> {
        const now = moment();
        const yesterday = now.subtract("1", "days");

        const query = `${environment.apiUrl}/readings/anomalies?starting_timestamp=${yesterday.toISOString()}`;
        const data = await fetch(query);

        return (await data.json()) ?? []
    }
}
