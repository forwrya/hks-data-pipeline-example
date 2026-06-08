import { Component, inject, signal } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { SensorReading } from './sensorreading';
import { ReadingsAPI } from './readings-api';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, AsyncPipe],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  readings: Promise<SensorReading[]>;
  readingsAPI: ReadingsAPI = inject(ReadingsAPI);

  constructor() {
    this.readings = this.readingsAPI.getRecentAnomalies();
  }
}
