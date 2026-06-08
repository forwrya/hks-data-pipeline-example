import { Component, inject } from '@angular/core';

import { MatTableModule, MatTableDataSource } from '@angular/material/table'
import { ScrollingModule } from '@angular/cdk/scrolling'

import { ReadingsAPI } from './readings-api';
import { AnomalySensorReading } from './anomaly-sensor-reading';

@Component({
  selector: 'app-root',
  imports: [MatTableModule, ScrollingModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  readingsAPI: ReadingsAPI = inject(ReadingsAPI);
  readingsDataSource: MatTableDataSource<AnomalySensorReading>;

  columnsToDisplay: string[];

  constructor() {
    this.readingsDataSource = new MatTableDataSource<AnomalySensorReading>([]);
    this.columnsToDisplay = [
      "anomaly_type",
      "confidence_score",
      "detected_at",
      "sensor_id",
      "timestamp",
      "temperature",
      "humidity",
      "pressure",
      "location"
    ];
    
    this.readingsAPI.getRecentAnomalies().then(readings => {

      // Make an entry per anomaly instead of per reading
      const flattenedAnomalies = [];
      for (const reading of readings) {

        const { anomalies, ...shared } = reading;
        for (const anomalyInfo of anomalies) {
          flattenedAnomalies.push({...anomalyInfo, ...shared});
        }
      }

      this.readingsDataSource.data = flattenedAnomalies;
    });
  }
}