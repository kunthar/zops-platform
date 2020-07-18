import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RocPricingComponent } from './roc-pricing.component';

describe('RocPricingComponent', () => {
  let component: RocPricingComponent;
  let fixture: ComponentFixture<RocPricingComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RocPricingComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RocPricingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
