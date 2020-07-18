import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SignupApproveComponent } from './signup-approve.component';

describe('SignupApproveComponent', () => {
  let component: SignupApproveComponent;
  let fixture: ComponentFixture<SignupApproveComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SignupApproveComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SignupApproveComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
