import { TestBed, inject } from '@angular/core/testing';

import { GetUserInfoService } from './get-user-info.service';

describe('GetUserInfoService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [GetUserInfoService]
    });
  });

  it('should be created', inject([GetUserInfoService], (service: GetUserInfoService) => {
    expect(service).toBeTruthy();
  }));
});
