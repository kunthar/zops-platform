import { TestBed, inject } from '@angular/core/testing';

import { SignupApproveService } from './signup-approve.service';

describe('SignupApproveService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [SignupApproveService]
    });
  });

  it('should be created', inject([SignupApproveService], (service: SignupApproveService) => {
    expect(service).toBeTruthy();
  }));
});
