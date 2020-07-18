import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShortFooterComponent } from './short-footer.component';

describe('ShortFooterComponent', () => {
  let component: ShortFooterComponent;
  let fixture: ComponentFixture<ShortFooterComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShortFooterComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShortFooterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
