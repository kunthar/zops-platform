import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { M2mComponent } from './m2m.component';

describe('M2mComponent', () => {
  let component: M2mComponent;
  let fixture: ComponentFixture<M2mComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ M2mComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(M2mComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
