import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { M2mHubComponent } from './m2m-hub.component';

describe('M2mHubComponent', () => {
  let component: M2mHubComponent;
  let fixture: ComponentFixture<M2mHubComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ M2mHubComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(M2mHubComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
