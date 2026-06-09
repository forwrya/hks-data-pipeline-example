import { TestBed } from '@angular/core/testing';

import { ReadingsAPI } from './readings-api';

describe('ReadingsAPI', () => {
  let service: ReadingsAPI;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ReadingsAPI);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
