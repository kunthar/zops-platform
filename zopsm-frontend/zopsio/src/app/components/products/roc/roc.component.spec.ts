import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RocComponent } from './roc.component';

describe('RocComponent', () => {
  let component: RocComponent;
  let fixture: ComponentFixture<RocComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RocComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RocComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
