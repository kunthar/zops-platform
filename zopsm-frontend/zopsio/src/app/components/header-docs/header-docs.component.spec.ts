import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { HeaderDocsComponent } from './header-docs.component';

describe('HeaderDocsComponent', () => {
  let component: HeaderDocsComponent;
  let fixture: ComponentFixture<HeaderDocsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HeaderDocsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HeaderDocsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
