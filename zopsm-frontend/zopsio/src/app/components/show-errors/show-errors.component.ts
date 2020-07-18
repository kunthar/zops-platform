import {Component, Input} from '@angular/core';
import {AbstractControlDirective, AbstractControl} from '@angular/forms';

@Component({
  selector: 'show-errors',
  template: `
    <div *ngIf="shouldShowErrors()">
      <div class="help-block" style="color: red" *ngFor="let error of listOfErrors()">{{error}}</div>
    </div>
  `,
})
export class ShowErrorsComponent {

  private static readonly errorMessages = {
    'required': () => 'This field is required!',
    'minlength': (params) => 'The min number of characters is ' + params.requiredLength + '!',
    'maxlength': (params) => 'The max allowed number of characters is ' + params.requiredLength + '!',
    'email': () => 'Email is invalid!'
  };

  @Input()
  private isFormSubmitted: boolean;

  @Input()
  private control: AbstractControlDirective | AbstractControl;

  shouldShowErrors(): boolean {
    return this.control &&
      this.control.errors &&
      (this.control.dirty || this.control.touched || this.isFormSubmitted);
  }

  listOfErrors(): string[] {
    return Object.keys(this.control.errors)
      .map(field => this.getMessage(field, this.control.errors[field]));
  }

  private getMessage(type: string, params: any) {
    return ShowErrorsComponent.errorMessages[type](params);
  }

}
