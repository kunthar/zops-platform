import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PushPricingComponent } from './push-pricing.component';

describe('PushPricingComponent', () => {
  let component: PushPricingComponent;
  let fixture: ComponentFixture<PushPricingComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PushPricingComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PushPricingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
