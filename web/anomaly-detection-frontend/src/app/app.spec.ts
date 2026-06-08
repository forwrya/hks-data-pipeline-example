import { TestBed } from '@angular/core/testing';
import { App } from './app';
import { MockBuilder } from 'ng-mocks';
import { ReadingsAPI } from './readings-api';

describe('App', () => {
  beforeEach(async () => {
    return MockBuilder(App, ReadingsAPI);
  });

  it('should create the app', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });
});
