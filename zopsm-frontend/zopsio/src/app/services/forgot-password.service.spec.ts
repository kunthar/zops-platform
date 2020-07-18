import { TestBed, inject } from '@angular/core/testing';

import { ForgotPasswordService } from './forgot-password.service';

describe('ForgotPasswordService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ForgotPasswordService]
    });
  });

  it('should be created', inject([ForgotPasswordService], (service: ForgotPasswordService) => {
    expect(service).toBeTruthy();
  }));
});
