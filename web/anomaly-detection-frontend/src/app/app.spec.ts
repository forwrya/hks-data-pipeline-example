import { TestBed } from '@angular/core/testing';
import { App } from './app';
import { MockBuilder, MockInstance } from 'ng-mocks';
import { ReadingsAPI } from './readings-api';

describe('App', () => {
  beforeEach(async () => {
    // Mock API to promise an empty array when getRecentAnomalies is called
    return MockInstance(ReadingsAPI, "getRecentAnomalies", () => {
      return Promise.resolve([]);
    })
  })

  beforeEach(async () => {
    return MockBuilder(App, ReadingsAPI);
  });

  it('should create the app', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });
});
