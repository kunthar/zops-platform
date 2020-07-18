import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { M2mPricingComponent } from './m2m-pricing.component';

describe('M2mPricingComponent', () => {
  let component: M2mPricingComponent;
  let fixture: ComponentFixture<M2mPricingComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ M2mPricingComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(M2mPricingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
