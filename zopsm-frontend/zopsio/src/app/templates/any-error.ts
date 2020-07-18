import {Component, Input} from "@angular/core";

@Component({
  selector: "any-error",
  template: `
    <div *ngIf="show" class="alert alert-danger alert-dismissible fade show" role="alert" style="margin: 20px 10px 10px;">
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
      <h4 class="alert-heading">Oops!</h4>
      <p>Looks like something went wrong. Check out our <a href="/help" class="alert-link">help</a> page.</p>
    </div>
  `,
})
export class AnyErrorTemplate {

  @Input()
  private show: boolean;
}

